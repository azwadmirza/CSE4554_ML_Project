def _import_module_from_path(module_name, plugin_path):
    """Imports `module_name` from `plugin_path`.

    Return None if no module is found.
    """
    module = None
    try:
        if PY2:
            info = imp.find_module(module_name, [plugin_path])
            if info:
                module = imp.load_module(module_name, *info)
        else:  # Python 3.4+
            spec = importlib.machinery.PathFinder.find_spec(
                module_name,
                [plugin_path])
            if spec:
                module = spec.loader.load_module(module_name)
    except Exception:
        pass

    return module