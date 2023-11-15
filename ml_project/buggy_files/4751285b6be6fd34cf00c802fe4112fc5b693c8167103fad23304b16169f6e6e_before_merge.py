    def __getattr__(self, name):
        """
        First try to get value from dynaconf then from Flask
        """
        try:
            return getattr(self._settings, name)
        except AttributeError:
            return self[name]