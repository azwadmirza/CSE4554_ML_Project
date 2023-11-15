    def setupenv(self):
        if self.envconfig._missing_subs:
            self.status = (
                "unresolvable substitution(s):\n    {}\n"
                "Environment variables are missing or defined recursively.".format(
                    "\n    ".join(
                        [
                            "{}: '{}'".format(section_key, exc.name)
                            for section_key, exc in sorted(self.envconfig._missing_subs.items())
                        ],
                    ),
                )
            )
            return
        if not self.matching_platform():
            self.status = "platform mismatch"
            return  # we simply omit non-matching platforms
        with self.new_action("getenv", self.envconfig.envdir) as action:
            self.status = 0
            default_ret_code = 1
            envlog = self.env_log
            try:
                status = self.update(action=action)
            except IOError as e:
                if e.args[0] != 2:
                    raise
                status = (
                    "Error creating virtualenv. Note that spaces in paths are "
                    "not supported by virtualenv. Error details: {!r}".format(e)
                )
            except tox.exception.InvocationError as e:
                status = e
            except tox.exception.InterpreterNotFound as e:
                status = e
                if self.envconfig.config.option.skip_missing_interpreters == "true":
                    default_ret_code = 0
            if status:
                str_status = str(status)
                command_log = envlog.get_commandlog("setup")
                command_log.add_command(["setup virtualenv"], str_status, default_ret_code)
                self.status = status
                if default_ret_code == 0:
                    reporter.skip(str_status)
                else:
                    reporter.error(str_status)
                return False
            command_path = self.getcommandpath("python")
            envlog.set_python_info(command_path)
            return True