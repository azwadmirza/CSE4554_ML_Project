    def load_extensions(self, key="EXTENSIONS", app=None):
        """Loads flask extensions dynamically."""
        app = app or self._app
        for extension in app.config[key]:
            # Split data in form `extension.path:factory_function`
            module_name, factory = extension.split(":")
            # Dynamically import extension module.
            ext = import_module(module_name)
            # Invoke factory passing app.
            getattr(ext, factory)(app)