    def cleanup(self):
        """Remove .ini files associated to configurations."""
        for _, config in self._configs_map.items():
            os.remove(config.get_config_fpath())