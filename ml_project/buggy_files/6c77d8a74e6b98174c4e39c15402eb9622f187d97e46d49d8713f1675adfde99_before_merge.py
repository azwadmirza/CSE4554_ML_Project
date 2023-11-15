    def _run_command(self, command, xfail=False):
        """Run a command that may or may not fail."""
        self.logger.info("==> {0}".format(command))
        try:
            subprocess.check_call(command)
            return 0
        except subprocess.CalledProcessError as e:
            if xfail:
                return e.returncode
            self.logger.error(
                'Failed GitHub deployment — command {0} '
                'returned {1}'.format(e.cmd, e.returncode)
            )
            raise SystemError(e.returncode)