    def _pcall(
        self,
        args,
        cwd,
        venv=True,
        is_test_command=False,
        action=None,
        redirect=True,
        ignore_ret=False,
    ):
        # construct environment variables
        os.environ.pop("VIRTUALENV_PYTHON", None)
        env = self._get_os_environ(is_test_command=is_test_command)
        bin_dir = str(self.envconfig.envbindir)
        env["PATH"] = os.pathsep.join([bin_dir, os.environ["PATH"]])
        self.session.report.verbosity2("setting PATH={}".format(env["PATH"]))

        # get command
        args[0] = self.getcommandpath(args[0], venv, cwd)
        if sys.platform != "win32" and "TOX_LIMITED_SHEBANG" in os.environ:
            args = prepend_shebang_interpreter(args)

        cwd.ensure(dir=1)  # ensure the cwd exists
        return action.popen(args, cwd=cwd, env=env, redirect=redirect, ignore_ret=ignore_ret)