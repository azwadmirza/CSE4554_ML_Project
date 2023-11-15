def import_plugins() -> None:
    """
    Imports the plugins found with `discover_plugins()`.
    """
    for module_name in DEFAULT_PLUGINS:
        try:
            # For default plugins we recursively import everything.
            import_module_and_submodules(module_name)
            logger.info("Plugin %s available", module_name)
        except ModuleNotFoundError:
            pass
    for module_name in discover_plugins():
        try:
            importlib.import_module(module_name)
            logger.info("Plugin %s available", module_name)
        except ModuleNotFoundError as e:
            logger.error(f"Plugin {module_name} could not be loaded: {e}")