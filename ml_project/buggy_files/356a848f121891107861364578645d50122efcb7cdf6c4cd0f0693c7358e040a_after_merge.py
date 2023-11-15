    def setupenv(self, venv):
        if venv.envconfig.missing_subs:
            venv.status = (
                "unresolvable substitution(s): %s. "
                "Environment variables are missing or defined recursively." %
                (','.join(["'%s'" % m for m in venv.envconfig.missing_subs])))
            return
        if not venv.matching_platform():
            venv.status = "platform mismatch"
            return  # we simply omit non-matching platforms
        action = self.newaction(venv, "getenv", venv.envconfig.envdir)
        with action:
            venv.status = 0
            envlog = self.resultlog.get_envlog(venv.name)
            try:
                status = venv.update(action=action)
            except IOError as e:
                if e.args[0] != 2:
                    raise
                status = (
                    "Error creating virtualenv. Note that spaces in paths are "
                    "not supported by virtualenv. Error details: %r" % e)
            except tox.exception.InvocationError as e:
                status = (
                    "Error creating virtualenv. Note that some special "
                    "characters (e.g. ':' and unicode symbols) in paths are "
                    "not supported by virtualenv. Error details: %r" % e)
            if status:
                commandlog = envlog.get_commandlog("setup")
                commandlog.add_command(["setup virtualenv"], str(status), 1)
                venv.status = status
                self.report.error(str(status))
                return False
            commandpath = venv.getcommandpath("python")
            envlog.set_python_info(commandpath)
            return True