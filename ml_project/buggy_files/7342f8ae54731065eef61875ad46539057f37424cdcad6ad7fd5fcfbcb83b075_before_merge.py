    def _needs_reinstall(self, setupdir, action):
        setup_py = setupdir.join("setup.py")
        setup_cfg = setupdir.join("setup.cfg")
        args = [self.envconfig.envpython, str(setup_py), "--name"]
        env = self._getenv()
        output = action.popen(args, cwd=setupdir, redirect=False, returnout=True, env=env)
        name = output.strip()
        args = [self.envconfig.envpython, "-c", "import sys; print(sys.path)"]
        out = action.popen(args, redirect=False, returnout=True, env=env)
        try:
            sys_path = ast.literal_eval(out.strip())
        except SyntaxError:
            sys_path = []
        egg_info_fname = ".".join((name, "egg-info"))
        for d in reversed(sys_path):
            egg_info = py.path.local(d).join(egg_info_fname)
            if egg_info.check():
                break
        else:
            return True
        needs_reinstall = any(
            conf_file.check() and conf_file.mtime() > egg_info.mtime()
            for conf_file in (setup_py, setup_cfg)
        )

        # Ensure the modification time of the egg-info folder is updated so we
        # won't need to do this again.
        # TODO(stephenfin): Remove once the minimum version of setuptools is
        # high enough to include https://github.com/pypa/setuptools/pull/1427/
        if needs_reinstall:
            egg_info.setmtime()

        return needs_reinstall