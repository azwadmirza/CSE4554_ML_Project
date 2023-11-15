    def ensure(self):
        """Ensure that a virtual environment exists, creating it if needed"""
        if not os.path.exists(self.path):
            logger.debug("%s does not exist; creating", self.path)
            self.create()
        elif not os.path.isdir(self.path):
            message = "%s exists but is not a directory" % self.path
            logger.error(message)
            raise VirtualEnvironmentError(message)
        elif not self._directory_is_venv():
            message = "Directory %s exists but is not a venv" % self.path
            logger.error(message)
            raise VirtualEnvironmentError(message)
        else:
            logger.debug("Found existing virtual environment at %s", self.path)

        self.ensure_interpreter()
        self.ensure_pip()