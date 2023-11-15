    def reset_shortcuts(self):
        """Reset keyboard shortcuts to default values."""
        self._user_config.reset_to_defaults(section='shortcuts')
        for plugin_config in self._plugin_configs:
            # TODO: check if the section exists?
            plugin_config.reset_to_defaults(section='shortcuts')