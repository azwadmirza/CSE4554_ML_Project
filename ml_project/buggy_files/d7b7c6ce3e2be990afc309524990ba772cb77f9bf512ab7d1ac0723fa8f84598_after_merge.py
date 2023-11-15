def _import_module_from_path(module_name, plugin_path):
    """Imports `module_name` from `plugin_path`.

    Return None if no module is found.
    """
    module = None
    if PY2:
        info = imp.find_module(module_name, [plugin_path])
        if info:
            module = imp.load_module(module_name, *info)
    elif sys.version_info[0:2] <= (3, 3):
        loader = importlib.machinery.PathFinder.find_module(
            module_name,
            [plugin_path])
        if loader:
            module = loader.load_module(module_name)
    else:  # Python 3.4+
        spec = importlib.machinery.PathFinder.find_spec(
            module_name,
            [plugin_path])
        if spec:
            # Needed to prevent an error when 'spec.loader' is None
            # See issue 6518
            try:
                module = spec.loader.load_module(module_name)
            except AttributeError:
                module = None
    return module