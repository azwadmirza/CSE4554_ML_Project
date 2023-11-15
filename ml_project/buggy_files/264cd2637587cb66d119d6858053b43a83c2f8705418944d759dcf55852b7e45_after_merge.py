    def copy(self):
        return DownloadConfig(ConfigObj(self.config, configspec=str(CONFIG_SPEC_PATH), default_encoding='utf-8'),
                              state_dir=self.state_dir)