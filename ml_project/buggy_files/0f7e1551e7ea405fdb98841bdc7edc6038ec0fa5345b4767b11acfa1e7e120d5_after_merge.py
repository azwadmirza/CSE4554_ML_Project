    def git(self, *args,
            stdin=None,
            working_dir=None,
            show_panel=False,
            throw_on_stderr=True,
            decode=True,
            encode=True,
            stdin_encoding="UTF-8",
            custom_environ=None):
        """
        Run the git command specified in `*args` and return the output
        of the git command as a string.

        If stdin is provided, it should be a string and will be piped to
        the git process.  If `working_dir` is provided, set this as the
        current working directory for the git process; otherwise,
        the `repo_path` value will be used.
        """
        args = self._include_global_flags(args)
        command = (self.git_binary_path, ) + tuple(arg for arg in args if arg)
        command_str = " ".join(command)

        show_panel_overrides = self.savvy_settings.get("show_panel_for")
        show_panel = show_panel or args[0] in show_panel_overrides

        close_panel_for = self.savvy_settings.get("close_panel_for") or []
        if args[0] in close_panel_for:
            sublime.active_window().run_command("hide_panel", {"cancel": True})

        live_panel_output = self.savvy_settings.get("live_panel_output", False)

        stdout, stderr = None, None

        try:
            if not working_dir:
                working_dir = self.repo_path
        except RuntimeError as e:
            # do not show panel when the window does not exist
            raise GitSavvyError(e, show_panel=False)
        except Exception as e:
            # offer initialization when "Not a git repository" is thrown from self.repo_path
            if type(e) == ValueError and e.args and "Not a git repository" in e.args[0]:
                sublime.set_timeout_async(
                    lambda: sublime.active_window().run_command("gs_offer_init"))
            raise GitSavvyError(e)

        try:
            startupinfo = None
            if os.name == "nt":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            environ = os.environ.copy()
            environ.update(custom_environ or {})
            start = time.time()
            p = subprocess.Popen(command,
                                 stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE,
                                 cwd=working_dir,
                                 env=environ,
                                 startupinfo=startupinfo)

            def initialize_panel():
                # clear panel
                util.log.panel("")
                if self.savvy_settings.get("show_stdin_in_output") and stdin is not None:
                    util.log.panel_append("STDIN\n{}\n".format(stdin))
                if self.savvy_settings.get("show_input_in_output"):
                    util.log.panel_append("> {}\n".format(command_str))

            if show_panel and live_panel_output:
                wrapper = LoggingProcessWrapper(p, self.savvy_settings.get("live_panel_output_timeout", 10000))
                initialize_panel()

            if stdin is not None and encode:
                stdin = stdin.encode(encoding=stdin_encoding)

            if show_panel and live_panel_output:
                stdout, stderr = wrapper.communicate(stdin)
            else:
                stdout, stderr = p.communicate(stdin)

            if decode:
                stdout, stderr = self.decode_stdout(stdout), self.decode_stdout(stderr)

            if show_panel and not live_panel_output:
                initialize_panel()
                if stdout:
                    util.log.panel_append(stdout)
                if stderr:
                    if stdout:
                        util.log.panel_append("\n")
                    util.log.panel_append(stderr)

        except Exception as e:
            # this should never be reached
            raise GitSavvyError("Please report this error to GitSavvy:\n\n{}\n\n{}".format(e, traceback.format_exc()))

        finally:
            end = time.time()
            if decode:
                util.debug.log_git(args, stdin, stdout, stderr, end - start)
            else:
                util.debug.log_git(
                    args,
                    stdin,
                    self.decode_stdout(stdout),
                    self.decode_stdout(stderr),
                    end - start
                )

            if show_panel and self.savvy_settings.get("show_time_elapsed_in_output", True):
                util.log.panel_append("\n[Done in {:.2f}s]".format(end - start))

        if throw_on_stderr and not p.returncode == 0:
            sublime.active_window().status_message(
                "Failed to run `git {}`. See log for details.".format(command[1])
            )

            if "*** Please tell me who you are." in stderr:
                sublime.set_timeout_async(
                    lambda: sublime.active_window().run_command("gs_setup_user"))

            if stdout or stderr:
                raise GitSavvyError("`{}` failed with following output:\n{}\n{}".format(
                    command_str, stdout, stderr
                ))
            else:
                raise GitSavvyError("`{}` failed.".format(command_str))

        return stdout