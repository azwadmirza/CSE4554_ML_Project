    def run_install_command(self, packages, action, options=()):
        argv = self.envconfig.install_command[:]
        i = argv.index("{packages}")
        argv[i : i + 1] = packages
        if "{opts}" in argv:
            i = argv.index("{opts}")
            argv[i : i + 1] = list(options)

        for x in ("PIP_RESPECT_VIRTUALENV", "PIP_REQUIRE_VIRTUALENV", "__PYVENV_LAUNCHER__"):
            os.environ.pop(x, None)

        if "PYTHONPATH" not in self.envconfig.passenv:
            # If PYTHONPATH not explicitly asked for, remove it.
            if "PYTHONPATH" in os.environ:
                self.session.report.warning(
                    "Discarding $PYTHONPATH from environment, to override "
                    "specify PYTHONPATH in 'passenv' in your configuration."
                )
                os.environ.pop("PYTHONPATH")

        old_stdout = sys.stdout
        sys.stdout = codecs.getwriter("utf8")(sys.stdout)
        try:
            self._pcall(
                argv,
                cwd=self.envconfig.config.toxinidir,
                action=action,
                redirect=self.session.report.verbosity < 2,
            )
        finally:
            sys.stdout = old_stdout