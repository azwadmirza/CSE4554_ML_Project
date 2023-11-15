    def network_config_path(self):
        return Path(DEFAULT_CONFIG_ROOT).joinpath(NODE_CONFIG_STORAGE_KEY, self.network)