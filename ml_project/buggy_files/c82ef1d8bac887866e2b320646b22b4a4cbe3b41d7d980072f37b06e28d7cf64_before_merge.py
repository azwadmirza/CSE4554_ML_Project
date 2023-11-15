    def setup_environment_overrides(self):
        '''Sets up overrides of the build environment'''

        for command_name in self.path_overrides:
            self._write_path_override(command_name, self.path_overrides[command_name])