def _run(
    cmd,
    cwd=None,
    stdin=None,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    output_encoding=None,
    output_loglevel="debug",
    log_callback=None,
    runas=None,
    group=None,
    shell=DEFAULT_SHELL,
    python_shell=False,
    env=None,
    clean_env=False,
    prepend_path=None,
    rstrip=True,
    template=None,
    umask=None,
    timeout=None,
    with_communicate=True,
    reset_system_locale=True,
    ignore_retcode=False,
    saltenv="base",
    pillarenv=None,
    pillar_override=None,
    use_vt=False,
    password=None,
    bg=False,
    encoded_cmd=False,
    success_retcodes=None,
    **kwargs
):
    """
    Do the DRY thing and only call subprocess.Popen() once
    """
    if "pillar" in kwargs and not pillar_override:
        pillar_override = kwargs["pillar"]
    if output_loglevel != "quiet" and _is_valid_shell(shell) is False:
        log.warning(
            "Attempt to run a shell command with what may be an invalid shell! "
            "Check to ensure that the shell <%s> is valid for this user.",
            shell,
        )

    output_loglevel = _check_loglevel(output_loglevel)
    log_callback = _check_cb(log_callback)
    use_sudo = False

    if runas is None and "__context__" in globals():
        runas = __context__.get("runas")

    if password is None and "__context__" in globals():
        password = __context__.get("runas_password")

    # Set the default working directory to the home directory of the user
    # salt-minion is running as. Defaults to home directory of user under which
    # the minion is running.
    if not cwd:
        cwd = os.path.expanduser("~{0}".format("" if not runas else runas))

        # make sure we can access the cwd
        # when run from sudo or another environment where the euid is
        # changed ~ will expand to the home of the original uid and
        # the euid might not have access to it. See issue #1844
        if not os.access(cwd, os.R_OK):
            cwd = "/"
            if salt.utils.platform.is_windows():
                cwd = os.path.abspath(os.sep)
    else:
        # Handle edge cases where numeric/other input is entered, and would be
        # yaml-ified into non-string types
        cwd = six.text_type(cwd)

    if bg:
        ignore_retcode = True
        use_vt = False

    if not salt.utils.platform.is_windows():
        if not os.path.isfile(shell) or not os.access(shell, os.X_OK):
            msg = "The shell {0} is not available".format(shell)
            raise CommandExecutionError(msg)
    if salt.utils.platform.is_windows() and use_vt:  # Memozation so not much overhead
        raise CommandExecutionError("VT not available on windows")

    if shell.lower().strip() == "powershell":
        # Strip whitespace
        if isinstance(cmd, six.string_types):
            cmd = cmd.strip()
        elif isinstance(cmd, list):
            cmd = " ".join(cmd).strip()

        # If we were called by script(), then fakeout the Windows
        # shell to run a Powershell script.
        # Else just run a Powershell command.
        stack = traceback.extract_stack(limit=2)

        # extract_stack() returns a list of tuples.
        # The last item in the list [-1] is the current method.
        # The third item[2] in each tuple is the name of that method.
        if stack[-2][2] == "script":
            cmd = "Powershell -NonInteractive -NoProfile -ExecutionPolicy Bypass {0}".format(
                cmd.replace('"', '\\"')
            )
        elif encoded_cmd:
            cmd = "Powershell -NonInteractive -EncodedCommand {0}".format(cmd)
        else:
            cmd = 'Powershell -NonInteractive -NoProfile "{0}"'.format(
                cmd.replace('"', '\\"')
            )

    # munge the cmd and cwd through the template
    (cmd, cwd) = _render_cmd(cmd, cwd, template, saltenv, pillarenv, pillar_override)
    ret = {}

    # If the pub jid is here then this is a remote ex or salt call command and needs to be
    # checked if blacklisted
    if "__pub_jid" in kwargs:
        if not _check_avail(cmd):
            raise CommandExecutionError(
                'The shell command "{0}" is not permitted'.format(cmd)
            )

    env = _parse_env(env)

    for bad_env_key in (x for x, y in six.iteritems(env) if y is None):
        log.error(
            "Environment variable '%s' passed without a value. "
            "Setting value to an empty string",
            bad_env_key,
        )
        env[bad_env_key] = ""

    def _get_stripped(cmd):
        # Return stripped command string copies to improve logging.
        if isinstance(cmd, list):
            return [x.strip() if isinstance(x, six.string_types) else x for x in cmd]
        elif isinstance(cmd, six.string_types):
            return cmd.strip()
        else:
            return cmd

    if output_loglevel is not None:
        # Always log the shell commands at INFO unless quiet logging is
        # requested. The command output is what will be controlled by the
        # 'loglevel' parameter.
        msg = "Executing command {0}{1}{0} {2}{3}in directory '{4}'{5}".format(
            "'" if not isinstance(cmd, list) else "",
            _get_stripped(cmd),
            "as user '{0}' ".format(runas) if runas else "",
            "in group '{0}' ".format(group) if group else "",
            cwd,
            ". Executing command in the background, no output will be " "logged."
            if bg
            else "",
        )
        log.info(log_callback(msg))

    if runas and salt.utils.platform.is_windows():
        if not HAS_WIN_RUNAS:
            msg = "missing salt/utils/win_runas.py"
            raise CommandExecutionError(msg)

        if isinstance(cmd, (list, tuple)):
            cmd = " ".join(cmd)

        return win_runas(cmd, runas, password, cwd)

    if runas and salt.utils.platform.is_darwin():
        # We need to insert the user simulation into the command itself and not
        # just run it from the environment on macOS as that method doesn't work
        # properly when run as root for certain commands.
        if isinstance(cmd, (list, tuple)):
            cmd = " ".join(map(_cmd_quote, cmd))

        # Ensure directory is correct before running command
        cmd = "cd -- {dir} && {{ {cmd}\n }}".format(dir=_cmd_quote(cwd), cmd=cmd)

        # Ensure environment is correct for a newly logged-in user by running
        # the command under bash as a login shell
        try:
            user_shell = __salt__["user.info"](runas)["shell"]
            if re.search("bash$", user_shell):
                cmd = "{shell} -l -c {cmd}".format(
                    shell=user_shell, cmd=_cmd_quote(cmd)
                )
        except KeyError:
            pass

        # Ensure the login is simulated correctly (note: su runs sh, not bash,
        # which causes the environment to be initialised incorrectly, which is
        # fixed by the previous line of code)
        cmd = "su -l {0} -c {1}".format(_cmd_quote(runas), _cmd_quote(cmd))

        # Set runas to None, because if you try to run `su -l` after changing
        # user, su will prompt for the password of the user and cause salt to
        # hang.
        runas = None

    if runas:
        # Save the original command before munging it
        try:
            pwd.getpwnam(runas)
        except KeyError:
            raise CommandExecutionError("User '{0}' is not available".format(runas))

    if group:
        if salt.utils.platform.is_windows():
            msg = "group is not currently available on Windows"
            raise SaltInvocationError(msg)
        if not which_bin(["sudo"]):
            msg = "group argument requires sudo but not found"
            raise CommandExecutionError(msg)
        try:
            grp.getgrnam(group)
        except KeyError:
            raise CommandExecutionError("Group '{0}' is not available".format(runas))
        else:
            use_sudo = True

    if runas or group:
        try:
            # Getting the environment for the runas user
            # Use markers to thwart any stdout noise
            # There must be a better way to do this.
            import uuid

            marker = "<<<" + str(uuid.uuid4()) + ">>>"
            marker_b = marker.encode(__salt_system_encoding__)
            py_code = (
                "import sys, os, itertools; "
                'sys.stdout.write("' + marker + '"); '
                'sys.stdout.write("\\0".join(itertools.chain(*os.environ.items()))); '
                'sys.stdout.write("' + marker + '");'
            )

            if use_sudo:
                env_cmd = ["sudo"]
                # runas is optional if use_sudo is set.
                if runas:
                    env_cmd.extend(["-u", runas])
                if group:
                    env_cmd.extend(["-g", group])
                if shell != DEFAULT_SHELL:
                    env_cmd.extend(["-s", "--", shell, "-c"])
                else:
                    env_cmd.extend(["-i", "--"])
                env_cmd.extend([sys.executable])
            elif __grains__["os"] in ["FreeBSD"]:
                env_cmd = (
                    "su",
                    "-",
                    runas,
                    "-c",
                    "{0} -c {1}".format(shell, sys.executable),
                )
            elif __grains__["os_family"] in ["Solaris"]:
                env_cmd = ("su", "-", runas, "-c", sys.executable)
            elif __grains__["os_family"] in ["AIX"]:
                env_cmd = ("su", "-", runas, "-c", sys.executable)
            else:
                env_cmd = ("su", "-s", shell, "-", runas, "-c", sys.executable)
            msg = "env command: {0}".format(env_cmd)
            log.debug(log_callback(msg))

            env_bytes, env_encoded_err = subprocess.Popen(
                env_cmd,
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE,
            ).communicate(salt.utils.stringutils.to_bytes(py_code))
            marker_count = env_bytes.count(marker_b)
            if marker_count == 0:
                # Possibly PAM prevented the login
                log.error(
                    "Environment could not be retrieved for user '%s': "
                    "stderr=%r stdout=%r",
                    runas,
                    env_encoded_err,
                    env_bytes,
                )
                # Ensure that we get an empty env_runas dict below since we
                # were not able to get the environment.
                env_bytes = b""
            elif marker_count != 2:
                raise CommandExecutionError(
                    "Environment could not be retrieved for user '{0}'",
                    info={"stderr": repr(env_encoded_err), "stdout": repr(env_bytes)},
                )
            else:
                # Strip the marker
                env_bytes = env_bytes.split(marker_b)[1]

            if six.PY2:
                import itertools

                env_runas = dict(itertools.izip(*[iter(env_bytes.split(b"\0"))] * 2))
            elif six.PY3:
                env_runas = dict(list(zip(*[iter(env_bytes.split(b"\0"))] * 2)))

            env_runas = dict(
                (salt.utils.stringutils.to_str(k), salt.utils.stringutils.to_str(v))
                for k, v in six.iteritems(env_runas)
            )
            env_runas.update(env)

            # Fix platforms like Solaris that don't set a USER env var in the
            # user's default environment as obtained above.
            if env_runas.get("USER") != runas:
                env_runas["USER"] = runas

            # Fix some corner cases where shelling out to get the user's
            # environment returns the wrong home directory.
            runas_home = os.path.expanduser("~{0}".format(runas))
            if env_runas.get("HOME") != runas_home:
                env_runas["HOME"] = runas_home

            env = env_runas
        except ValueError as exc:
            log.exception("Error raised retrieving environment for user %s", runas)
            raise CommandExecutionError(
                "Environment could not be retrieved for user '{0}': {1}".format(
                    runas, exc
                )
            )

    if reset_system_locale is True:
        if not salt.utils.platform.is_windows():
            # Default to C!
            # Salt only knows how to parse English words
            # Don't override if the user has passed LC_ALL
            env.setdefault("LC_CTYPE", "C")
            env.setdefault("LC_NUMERIC", "C")
            env.setdefault("LC_TIME", "C")
            env.setdefault("LC_COLLATE", "C")
            env.setdefault("LC_MONETARY", "C")
            env.setdefault("LC_MESSAGES", "C")
            env.setdefault("LC_PAPER", "C")
            env.setdefault("LC_NAME", "C")
            env.setdefault("LC_ADDRESS", "C")
            env.setdefault("LC_TELEPHONE", "C")
            env.setdefault("LC_MEASUREMENT", "C")
            env.setdefault("LC_IDENTIFICATION", "C")
            env.setdefault("LANGUAGE", "C")
        else:
            # On Windows set the codepage to US English.
            if python_shell:
                cmd = "chcp 437 > nul & " + cmd

    if clean_env:
        run_env = env

    else:
        if salt.utils.platform.is_windows():
            import nt

            run_env = nt.environ.copy()
        else:
            run_env = os.environ.copy()
        run_env.update(env)

    if prepend_path:
        run_env["PATH"] = ":".join((prepend_path, run_env["PATH"]))

    if python_shell is None:
        python_shell = False

    new_kwargs = {
        "cwd": cwd,
        "shell": python_shell,
        "env": run_env if six.PY3 else salt.utils.data.encode(run_env),
        "stdin": six.text_type(stdin) if stdin is not None else stdin,
        "stdout": stdout,
        "stderr": stderr,
        "with_communicate": with_communicate,
        "timeout": timeout,
        "bg": bg,
    }

    if "stdin_raw_newlines" in kwargs:
        new_kwargs["stdin_raw_newlines"] = kwargs["stdin_raw_newlines"]

    if umask is not None:
        _umask = six.text_type(umask).lstrip("0")

        if _umask == "":
            msg = "Zero umask is not allowed."
            raise CommandExecutionError(msg)

        try:
            _umask = int(_umask, 8)
        except ValueError:
            raise CommandExecutionError("Invalid umask: '{0}'".format(umask))
    else:
        _umask = None

    if runas or group or umask:
        new_kwargs["preexec_fn"] = functools.partial(
            salt.utils.user.chugid_and_umask, runas, _umask, group
        )

    if not salt.utils.platform.is_windows():
        # close_fds is not supported on Windows platforms if you redirect
        # stdin/stdout/stderr
        if new_kwargs["shell"] is True:
            new_kwargs["executable"] = shell
        new_kwargs["close_fds"] = True

    if not os.path.isabs(cwd) or not os.path.isdir(cwd):
        raise CommandExecutionError(
            "Specified cwd '{0}' either not absolute or does not exist".format(cwd)
        )

    if (
        python_shell is not True
        and not salt.utils.platform.is_windows()
        and not isinstance(cmd, list)
    ):
        cmd = salt.utils.args.shlex_split(cmd)

    if success_retcodes is None:
        success_retcodes = [0]
    else:
        try:
            success_retcodes = [
                int(i) for i in salt.utils.args.split_input(success_retcodes)
            ]
        except ValueError:
            raise SaltInvocationError("success_retcodes must be a list of integers")
    if not use_vt:
        # This is where the magic happens
        try:
            proc = salt.utils.timed_subprocess.TimedProc(cmd, **new_kwargs)
        except (OSError, IOError) as exc:
            msg = (
                "Unable to run command '{0}' with the context '{1}', "
                "reason: {2}".format(
                    cmd if output_loglevel is not None else "REDACTED", new_kwargs, exc
                )
            )
            raise CommandExecutionError(msg)

        try:
            proc.run()
        except TimedProcTimeoutError as exc:
            ret["stdout"] = six.text_type(exc)
            ret["stderr"] = ""
            ret["retcode"] = None
            ret["pid"] = proc.process.pid
            # ok return code for timeouts?
            ret["retcode"] = 1
            return ret

        if output_loglevel != "quiet" and output_encoding is not None:
            log.debug(
                "Decoding output from command %s using %s encoding",
                cmd,
                output_encoding,
            )

        try:
            out = salt.utils.stringutils.to_unicode(
                proc.stdout, encoding=output_encoding
            )
        except TypeError:
            # stdout is None
            out = ""
        except UnicodeDecodeError:
            out = salt.utils.stringutils.to_unicode(
                proc.stdout, encoding=output_encoding, errors="replace"
            )
            if output_loglevel != "quiet":
                log.error(
                    "Failed to decode stdout from command %s, non-decodable "
                    "characters have been replaced",
                    cmd,
                )

        try:
            err = salt.utils.stringutils.to_unicode(
                proc.stderr, encoding=output_encoding
            )
        except TypeError:
            # stderr is None
            err = ""
        except UnicodeDecodeError:
            err = salt.utils.stringutils.to_unicode(
                proc.stderr, encoding=output_encoding, errors="replace"
            )
            if output_loglevel != "quiet":
                log.error(
                    "Failed to decode stderr from command %s, non-decodable "
                    "characters have been replaced",
                    cmd,
                )

        if rstrip:
            if out is not None:
                out = out.rstrip()
            if err is not None:
                err = err.rstrip()
        ret["pid"] = proc.process.pid
        ret["retcode"] = proc.process.returncode
        if ret["retcode"] in success_retcodes:
            ret["retcode"] = 0
        ret["stdout"] = out
        ret["stderr"] = err
    else:
        formatted_timeout = ""
        if timeout:
            formatted_timeout = " (timeout: {0}s)".format(timeout)
        if output_loglevel is not None:
            msg = "Running {0} in VT{1}".format(cmd, formatted_timeout)
            log.debug(log_callback(msg))
        stdout, stderr = "", ""
        now = time.time()
        if timeout:
            will_timeout = now + timeout
        else:
            will_timeout = -1
        try:
            proc = salt.utils.vt.Terminal(
                cmd,
                shell=True,
                log_stdout=True,
                log_stderr=True,
                cwd=cwd,
                preexec_fn=new_kwargs.get("preexec_fn", None),
                env=run_env,
                log_stdin_level=output_loglevel,
                log_stdout_level=output_loglevel,
                log_stderr_level=output_loglevel,
                stream_stdout=True,
                stream_stderr=True,
            )
            ret["pid"] = proc.pid
            while proc.has_unread_data:
                try:
                    try:
                        time.sleep(0.5)
                        try:
                            cstdout, cstderr = proc.recv()
                        except IOError:
                            cstdout, cstderr = "", ""
                        if cstdout:
                            stdout += cstdout
                        else:
                            cstdout = ""
                        if cstderr:
                            stderr += cstderr
                        else:
                            cstderr = ""
                        if timeout and (time.time() > will_timeout):
                            ret["stderr"] = ("SALT: Timeout after {0}s\n{1}").format(
                                timeout, stderr
                            )
                            ret["retcode"] = None
                            break
                    except KeyboardInterrupt:
                        ret["stderr"] = "SALT: User break\n{0}".format(stderr)
                        ret["retcode"] = 1
                        break
                except salt.utils.vt.TerminalException as exc:
                    log.error("VT: %s", exc, exc_info_on_loglevel=logging.DEBUG)
                    ret = {"retcode": 1, "pid": "2"}
                    break
                # only set stdout on success as we already mangled in other
                # cases
                ret["stdout"] = stdout
                if not proc.isalive():
                    # Process terminated, i.e., not canceled by the user or by
                    # the timeout
                    ret["stderr"] = stderr
                    ret["retcode"] = proc.exitstatus
                    if ret["retcode"] in success_retcodes:
                        ret["retcode"] = 0
                ret["pid"] = proc.pid
        finally:
            proc.close(terminate=True, kill=True)
    try:
        if ignore_retcode:
            __context__["retcode"] = 0
        else:
            __context__["retcode"] = ret["retcode"]
    except NameError:
        # Ignore the context error during grain generation
        pass

    # Log the output
    if output_loglevel is not None:
        if not ignore_retcode and ret["retcode"] != 0:
            if output_loglevel < LOG_LEVELS["error"]:
                output_loglevel = LOG_LEVELS["error"]
            msg = "Command '{0}' failed with return code: {1}".format(
                cmd, ret["retcode"]
            )
            log.error(log_callback(msg))
        if ret["stdout"]:
            log.log(output_loglevel, "stdout: %s", log_callback(ret["stdout"]))
        if ret["stderr"]:
            log.log(output_loglevel, "stderr: %s", log_callback(ret["stderr"]))
        if ret["retcode"]:
            log.log(output_loglevel, "retcode: %s", ret["retcode"])

    return ret