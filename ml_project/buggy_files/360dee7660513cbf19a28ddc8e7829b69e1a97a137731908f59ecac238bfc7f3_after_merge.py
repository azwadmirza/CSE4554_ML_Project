    def _create_dir(self):
        """
        Creates configuration directory if it does not already exist, otherwise does nothing.
        May raise an OSError if we do not have permissions to create the directory.
        """
        self.config_dir.mkdir(mode=0o700, parents=True, exist_ok=True)