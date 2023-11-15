    def setup_config(self):
        return salt.config.api_config(self.get_config_file_path())  # pylint: disable=no-member