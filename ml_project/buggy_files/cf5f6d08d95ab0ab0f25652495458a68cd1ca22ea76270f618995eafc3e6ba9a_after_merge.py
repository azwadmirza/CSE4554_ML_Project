    def load_extensions(self, key="EXTENSIONS", app=None):
        """Loads flask extensions dynamically."""
        app = app or self._app
        extensions = app.config.get(key)
        if not extensions:
            warnings.warn(
                f"Settings is missing {key} to load Flask Extensions",
                RuntimeWarning,
            )
            return

        for extension in app.config[key]:
            # Split data in form `extension.path:factory_function`
            module_name, factory = extension.split(":")
            # Dynamically import extension module.
            ext = import_module(module_name)
            # Invoke factory passing app.
            getattr(ext, factory)(app)