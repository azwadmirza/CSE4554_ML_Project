    def import_module(config):
        """Import module namespace as variable and return it."""
        # Check if the module can be imported and proceed with import

        # Proceed only if config.name is specified
        # and parent module can be imported
        if config["name"] and importlib.util.find_spec(config["module_path"]):
            module_spec = importlib.util.find_spec(config["module_path"] +
                                                   "." + config["name"])
            if module_spec:
                module = Loader.import_module_from_spec(module_spec)
                _LOGGER.debug("Loaded %s: %s", config["type"],
                              config["module_path"])
                return module

        module_spec = importlib.util.find_spec(config["module_path"])
        if module_spec:
            module = Loader.import_module_from_spec(module_spec)
            _LOGGER.debug("Loaded %s: %s", config["type"],
                          config["module_path"])
            return module

        _LOGGER.error("Failed to load %s: %s", config["type"],
                      config["module_path"])

        return None