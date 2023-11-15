    def run_install_command(self, packages, action, options=()):
        def expand(val):
            # expand an install command
            if val == "{packages}":
                for package in packages:
                    yield package
            elif val == "{opts}":
                for opt in options:
                    yield opt
            else:
                yield val

        cmd = list(chain.from_iterable(expand(val) for val in self.envconfig.install_command))

        self.ensure_pip_os_environ_ok()

        old_stdout = sys.stdout
        sys.stdout = codecs.getwriter("utf8")(sys.stdout)
        try:
            self._pcall(
                cmd,
                cwd=self.envconfig.config.toxinidir,
                action=action,
                redirect=self.session.report.verbosity < 2,
            )
        finally:
            sys.stdout = old_stdout