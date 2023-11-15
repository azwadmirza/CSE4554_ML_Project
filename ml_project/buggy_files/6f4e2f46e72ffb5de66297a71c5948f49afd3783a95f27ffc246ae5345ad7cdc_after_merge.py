    def get(self, key, default=None):
        try:
            return get_project_settings(self._window)[key]
        except KeyError:
            return self._global_settings.get(key, default)