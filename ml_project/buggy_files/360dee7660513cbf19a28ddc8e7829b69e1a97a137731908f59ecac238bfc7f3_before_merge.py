    def _create_dir(self):
        self.config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)