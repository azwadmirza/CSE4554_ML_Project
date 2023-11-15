    def iter_shortcuts(self):
        """Iterate over keyboard shortcuts."""
        for context_name, keystr in self._user_config.items('shortcuts'):
            context, name = context_name.split('/', 1)
            yield context, name, keystr

        for _, (_, plugin_config) in self._plugin_configs.items():
            items = plugin_config.items('shortcuts')
            if items:
                for context_name, keystr in items:
                    context, name = context_name.split('/', 1)
                    yield context, name, keystr