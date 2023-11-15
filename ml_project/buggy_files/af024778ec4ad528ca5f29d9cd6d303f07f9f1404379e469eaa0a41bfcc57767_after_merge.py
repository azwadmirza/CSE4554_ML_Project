    def settings_module(self):
        """Gets SETTINGS_MODULE variable"""
        settings_module = os.environ.get(
            self.ENVVAR_FOR_DYNACONF,
            self.SETTINGS_MODULE_FOR_DYNACONF
        )
        if settings_module != getattr(self, 'SETTINGS_MODULE', None):
            self.set('SETTINGS_MODULE', settings_module)
        return self.SETTINGS_MODULE