    def __getitem__(self, key):
        try:
            return self._settings[key]
        except KeyError:
            return Config.__getitem__(self, key)