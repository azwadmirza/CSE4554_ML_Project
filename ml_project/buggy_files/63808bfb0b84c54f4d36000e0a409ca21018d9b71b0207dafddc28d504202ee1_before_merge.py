    def cleanup(self):
        """Remove .ini files associated to configurations."""
        for config in self._configs_map:
            os.remove(config.get_config_fpath())