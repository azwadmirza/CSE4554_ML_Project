    def import_module(config):
        """Import module namespace as variable and return it."""
        try:
            module = importlib.import_module(
                config["module_path"] + "." + config["name"])
            _LOGGER.debug("Loaded %s: %s", config["type"],
                          config["module_path"])
            return module

        except ImportError as error:
            _LOGGER.debug("Failed to load %s.%s.  ERROR: %s",
                          config["module_path"], config["name"], error)

        try:
            module = importlib.import_module(
                config["module_path"])
            _LOGGER.debug("Loaded %s: %s", config["type"],
                          config["module_path"])
            return module

        except ImportError as error:
            _LOGGER.error("Failed to load %s: %s", config["type"],
                          config["module_path"])
            _LOGGER.debug(error)

        return None