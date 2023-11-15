    def _pcall(
        self, args, cwd, venv=True, testcommand=False, action=None, redirect=True, ignore_ret=False
    ):
        os.environ.pop("VIRTUALENV_PYTHON", None)

        cwd.ensure(dir=1)
        args[0] = self.getcommandpath(args[0], venv, cwd)
        if sys.platform != "win32" and "TOX_LIMITED_SHEBANG" in os.environ:
            args = prepend_shebang_interpreter(args)
        env = self._getenv(testcommand=testcommand)
        bindir = str(self.envconfig.envbindir)
        env["PATH"] = p = os.pathsep.join([bindir, os.environ["PATH"]])
        self.session.report.verbosity2("setting PATH={}".format(p))
        return action.popen(args, cwd=cwd, env=env, redirect=redirect, ignore_ret=ignore_ret)