    def init_app(self, app, **kwargs):
        """kwargs holds initial dynaconf configuration"""
        self.kwargs.update(kwargs)
        self.settings = self.dynaconf_instance or dynaconf.LazySettings(
            **self.kwargs
        )
        dynaconf.settings = self.settings  # rebind customized settings
        app.config = self.make_config(app)
        app.dynaconf = self.settings