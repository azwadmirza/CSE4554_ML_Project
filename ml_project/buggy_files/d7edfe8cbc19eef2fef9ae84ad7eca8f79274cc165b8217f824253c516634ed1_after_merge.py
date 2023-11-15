    def main(self, args, env_vars=None, shim=None):
        # type: (List[str], EnvVars, OptStr) -> Tuple[int, Optional[bytes]]
        if env_vars is None:
            env_vars = self._osutils.environ()
        if shim is None:
            shim = ''
        python_exe = sys.executable
        run_pip = (
            'import sys; %s; sys.exit(main(%s))'
        ) % (self._import_string, args)
        exec_string = '%s%s' % (shim, run_pip)
        invoke_pip = [python_exe, '-c', exec_string]
        p = self._osutils.popen(invoke_pip,
                                stdout=self._osutils.pipe,
                                stderr=self._osutils.pipe,
                                env=env_vars)
        _, err = p.communicate()
        rc = p.returncode
        return rc, err