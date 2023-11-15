    def write(self):
        """
        Write the configuration to the config file in the state dir as specified in the config.
        """
        state_dir = self.get_state_dir()
        if not state_dir.exists():
            os.makedirs(state_dir, exist_ok=True)
        self.config.filename = state_dir / CONFIG_FILENAME
        self.config.write()