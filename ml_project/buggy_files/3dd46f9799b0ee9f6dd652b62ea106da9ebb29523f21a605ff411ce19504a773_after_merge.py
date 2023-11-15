def _run(cmd,
         cwd=None,
         stdin=None,
         stdout=subprocess.PIPE,
         stderr=subprocess.PIPE,
         output_loglevel='debug',
         log_callback=None,
         runas=None,
         shell=DEFAULT_SHELL,
         python_shell=False,
         env=None,
         clean_env=False,
         rstrip=True,
         template=None,
         umask=None,
         timeout=None,
         with_communicate=True,
         reset_system_locale=True,
         ignore_retcode=False,
         saltenv='base',
         pillarenv=None,
         pillar_override=None,
         use_vt=False):
    '''
    Do the DRY thing and only call subprocess.Popen() once
    '''
    if _is_valid_shell(shell) is False:
        log.warning(
            'Attempt to run a shell command with what may be an invalid shell! '
            'Check to ensure that the shell <{0}> is valid for this user.'
            .format(shell))

    log_callback = _check_cb(log_callback)

    # Set the default working directory to the home directory of the user
    # salt-minion is running as. Defaults to home directory of user under which
    # the minion is running.
    if not cwd:
        cwd = os.path.expanduser('~{0}'.format('' if not runas else runas))

        # make sure we can access the cwd
        # when run from sudo or another environment where the euid is
        # changed ~ will expand to the home of the original uid and
        # the euid might not have access to it. See issue #1844
        if not os.access(cwd, os.R_OK):
            cwd = '/'
            if salt.utils.is_windows():
                cwd = os.tempnam()[:3]
    else:
        # Handle edge cases where numeric/other input is entered, and would be
        # yaml-ified into non-string types
        cwd = str(cwd)

    if not salt.utils.is_windows():
        if not os.path.isfile(shell) or not os.access(shell, os.X_OK):
            msg = 'The shell {0} is not available'.format(shell)
            raise CommandExecutionError(msg)
    if salt.utils.is_windows() and use_vt:  # Memozation so not much overhead
        raise CommandExecutionError('VT not available on windows')

    if shell.lower().strip() == 'powershell':
        # If we were called by script(), then fakeout the Windows
        # shell to run a Powershell script.
        # Else just run a Powershell command.
        stack = traceback.extract_stack(limit=2)

        # extract_stack() returns a list of tuples.
        # The last item in the list [-1] is the current method.
        # The third item[2] in each tuple is the name of that method.
        if stack[-2][2] == 'script':
            cmd = 'Powershell -NonInteractive -ExecutionPolicy Bypass -File ' + cmd
        else:
            cmd = 'Powershell -NonInteractive "{0}"'.format(cmd.replace('"', '\\"'))

    # munge the cmd and cwd through the template
    (cmd, cwd) = _render_cmd(cmd, cwd, template, saltenv, pillarenv, pillar_override)

    ret = {}

    env = _parse_env(env)

    for bad_env_key in (x for x, y in six.iteritems(env) if y is None):
        log.error('Environment variable {0!r} passed without a value. '
                  'Setting value to an empty string'.format(bad_env_key))
        env[bad_env_key] = ''

    if runas and salt.utils.is_windows():
        # TODO: Figure out the proper way to do this in windows
        msg = 'Sorry, {0} does not support runas functionality'
        raise CommandExecutionError(msg.format(__grains__['os']))

    if runas:
        # Save the original command before munging it
        try:
            pwd.getpwnam(runas)
        except KeyError:
            raise CommandExecutionError(
                'User {0!r} is not available'.format(runas)
            )
        try:
            # Getting the environment for the runas user
            # There must be a better way to do this.
            py_code = (
                'import sys, os, itertools; '
                'sys.stdout.write(\"\\0\".join(itertools.chain(*os.environ.items())))'
            )
            if __grains__['os'] in ['MacOS', 'Darwin']:
                env_cmd = ('sudo', '-i', '-u', runas, '--',
                           sys.executable)
            elif __grains__['os'] in ['FreeBSD']:
                env_cmd = ('su', '-', runas, '-c',
                           "{0} -c {1}".format(shell, sys.executable))
            elif __grains__['os_family'] in ['Solaris']:
                env_cmd = ('su', '-', runas, '-c', sys.executable)
            elif __grains__['os_family'] in ['AIX']:
                env_cmd = ('su', runas, '-c', sys.executable)
            else:
                env_cmd = ('su', '-s', shell, '-', runas, '-c', sys.executable)
            env_encoded = subprocess.Popen(
                env_cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE
            ).communicate(py_code)[0]
            import itertools
            env_runas = dict(itertools.izip(*[iter(env_encoded.split(b'\0'))]*2))
            env_runas.update(env)
            env = env_runas
            # Encode unicode kwargs to filesystem encoding to avoid a
            # UnicodeEncodeError when the subprocess is invoked.
            fse = sys.getfilesystemencoding()
            for key, val in six.iteritems(env):
                if isinstance(val, six.text_type):
                    env[key] = val.encode(fse)
        except ValueError:
            raise CommandExecutionError(
                'Environment could not be retrieved for User {0!r}'.format(
                    runas
                )
            )

    if _check_loglevel(output_loglevel) is not None:
        # Always log the shell commands at INFO unless quiet logging is
        # requested. The command output is what will be controlled by the
        # 'loglevel' parameter.
        msg = (
            'Executing command {0!r} {1}in directory {2!r}'.format(
                cmd, 'as user {0!r} '.format(runas) if runas else '', cwd
            )
        )
        log.info(log_callback(msg))

    if reset_system_locale is True:
        if not salt.utils.is_windows():
            # Default to C!
            # Salt only knows how to parse English words
            # Don't override if the user has passed LC_ALL
            env.setdefault('LC_ALL', 'C')
        else:
            # On Windows set the codepage to US English.
            if python_shell:
                cmd = 'chcp 437 > nul & ' + cmd

    if clean_env:
        run_env = env

    else:
        run_env = os.environ.copy()
        run_env.update(env)

    if python_shell is None:
        python_shell = False

    kwargs = {'cwd': cwd,
              'shell': python_shell,
              'env': run_env,
              'stdin': str(stdin) if stdin is not None else stdin,
              'stdout': stdout,
              'stderr': stderr,
              'with_communicate': with_communicate}

    if umask is not None:
        _umask = str(umask).lstrip('0')

        if _umask == '':
            msg = 'Zero umask is not allowed.'
            raise CommandExecutionError(msg)

        try:
            _umask = int(_umask, 8)
        except ValueError:
            msg = 'Invalid umask: \'{0}\''.format(umask)
            raise CommandExecutionError(msg)
    else:
        _umask = None

    if runas or umask:
        kwargs['preexec_fn'] = functools.partial(
            salt.utils.chugid_and_umask,
            runas,
            _umask)

    if not salt.utils.is_windows():
        # close_fds is not supported on Windows platforms if you redirect
        # stdin/stdout/stderr
        if kwargs['shell'] is True:
            kwargs['executable'] = shell
        kwargs['close_fds'] = True

    if not os.path.isabs(cwd) or not os.path.isdir(cwd):
        raise CommandExecutionError(
            'Specified cwd {0!r} either not absolute or does not exist'
            .format(cwd)
        )

    if python_shell is not True and not isinstance(cmd, list):
        posix = True
        if salt.utils.is_windows():
            posix = False
        cmd = shlex.split(cmd, posix=posix)
    if not use_vt:
        # This is where the magic happens
        try:
            proc = salt.utils.timed_subprocess.TimedProc(cmd, **kwargs)
        except (OSError, IOError) as exc:
            raise CommandExecutionError(
                'Unable to run command {0!r} with the context {1!r}, reason: {2}'
                .format(cmd, kwargs, exc)
            )

        try:
            proc.wait(timeout)
        except TimedProcTimeoutError as exc:
            ret['stdout'] = str(exc)
            ret['stderr'] = ''
            ret['retcode'] = None
            ret['pid'] = proc.process.pid
            # ok return code for timeouts?
            ret['retcode'] = 1
            return ret

        out, err = proc.stdout, proc.stderr
        if err is None:
            # Will happen if redirect_stderr is True, since stderr was sent to
            # stdout.
            err = ''

        if rstrip:
            if out is not None:
                out = salt.utils.to_str(out).rstrip()
            if err is not None:
                err = salt.utils.to_str(err).rstrip()
        ret['pid'] = proc.process.pid
        ret['retcode'] = proc.process.returncode
        ret['stdout'] = out
        ret['stderr'] = err
    else:
        to = ''
        if timeout:
            to = ' (timeout: {0}s)'.format(timeout)
        if _check_loglevel(output_loglevel) is not None:
            msg = 'Running {0} in VT{1}'.format(cmd, to)
            log.debug(log_callback(msg))
        stdout, stderr = '', ''
        now = time.time()
        if timeout:
            will_timeout = now + timeout
        else:
            will_timeout = -1
        try:
            proc = vt.Terminal(cmd,
                               shell=True,
                               log_stdout=True,
                               log_stderr=True,
                               cwd=cwd,
                               preexec_fn=kwargs.get('preexec_fn', None),
                               env=run_env,
                               log_stdin_level=output_loglevel,
                               log_stdout_level=output_loglevel,
                               log_stderr_level=output_loglevel,
                               stream_stdout=True,
                               stream_stderr=True)
            ret['pid'] = proc.pid
            while proc.has_unread_data:
                try:
                    try:
                        time.sleep(0.5)
                        try:
                            cstdout, cstderr = proc.recv()
                        except IOError:
                            cstdout, cstderr = '', ''
                        if cstdout:
                            stdout += cstdout
                        else:
                            cstdout = ''
                        if cstderr:
                            stderr += cstderr
                        else:
                            cstderr = ''
                        if timeout and (time.time() > will_timeout):
                            ret['stderr'] = (
                                'SALT: Timeout after {0}s\n{1}').format(
                                    timeout, stderr)
                            ret['retcode'] = None
                            break
                    except KeyboardInterrupt:
                        ret['stderr'] = 'SALT: User break\n{0}'.format(stderr)
                        ret['retcode'] = 1
                        break
                except vt.TerminalException as exc:
                    log.error(
                        'VT: {0}'.format(exc),
                        exc_info_on_loglevel=logging.DEBUG)
                    ret = {'retcode': 1, 'pid': '2'}
                    break
                # only set stdout on success as we already mangled in other
                # cases
                ret['stdout'] = stdout
                if not proc.isalive():
                    # Process terminated, i.e., not canceled by the user or by
                    # the timeout
                    ret['stderr'] = stderr
                    ret['retcode'] = proc.exitstatus
                ret['pid'] = proc.pid
        finally:
            proc.close(terminate=True, kill=True)
    try:
        if ignore_retcode:
            __context__['retcode'] = 0
        else:
            __context__['retcode'] = ret['retcode']
    except NameError:
        # Ignore the context error during grain generation
        pass
    return ret