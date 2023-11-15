    def _run_subprocess(self, *args, append_environ=None, **kwargs):
        new_env = dict(os.environ)
        if "PATH" not in new_env:
            new_env["PATH"] = os.defpath
        if len(new_env["PATH"]) > 0 and not new_env["PATH"].startswith(os.pathsep):
            new_env["PATH"] = os.pathsep + new_env["PATH"]
        new_env["PATH"] = str(self._path_overrides_dir.absolute()) + new_env["PATH"]
        if not append_environ is None:
            new_env.update(append_environ)
        kwargs["env"] = new_env
        return _util.subprocess_run(*args, **kwargs)