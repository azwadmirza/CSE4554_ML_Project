    def setup_environment_overrides(self):
        '''Sets up overrides of the build environment'''

        self.logger.info("Setting up environment overrides...")

        for command_name in self.path_overrides:
            self.logger.debug("Setting command '{}' as '{}'".format(
                command_name, self.path_overrides[command_name]))
            self._write_path_override(command_name, self.path_overrides[command_name])