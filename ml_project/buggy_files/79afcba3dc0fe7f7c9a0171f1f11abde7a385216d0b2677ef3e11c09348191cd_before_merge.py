    def iter_shortcuts(self):
        """Iterate over keyboard shortcuts."""
        for context_name, keystr in self._user_config.items('shortcuts'):
            context, name = context_name.split('/', 1)
            yield context, name, keystr

        for p_section, (p_class, p_config) in self._plugin_configs.items():
            items = p_config.items('shortcuts')
            if items:
                for context_name, keystr in items:
                    context, name = context_name.split('/', 1)
                    yield context, name, keystr