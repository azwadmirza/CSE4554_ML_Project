    def _load_config_file(self, config_file_path: str) -> ConfigObj:
        return ConfigObj(infile=config_file_path, configspec=str(CONFIG_SPEC_PATH), default_encoding='utf-8')