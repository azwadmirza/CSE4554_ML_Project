    def write(self):
        """
        Write the configuration to the config file in the state dir as specified in the config.
        """
        if not self.get_state_dir().exists():
            os.makedirs(self.get_state_dir())
        self.config.filename = self.get_state_dir() / CONFIG_FILENAME
        self.config.write()