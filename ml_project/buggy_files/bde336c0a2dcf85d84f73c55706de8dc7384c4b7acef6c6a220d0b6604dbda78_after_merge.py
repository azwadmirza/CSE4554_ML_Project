def try_to_load_from_py_module_name(
    obj, name, key=None, identifier="py", silent=False
):
    """Try to load module by its string name.

    Arguments:
        obj {LAzySettings} -- Dynaconf settings instance
        name {str} -- Name of the module e.g: foo.bar.zaz

    Keyword Arguments:
        key {str} -- Single key to be loaded (default: {None})
        identifier {str} -- Name of identifier to store (default: 'py')
        silent {bool} -- Weather to raise or silence exceptions.
    """
    ctx = suppress(ImportError, TypeError) if silent else suppress()

    with ctx:
        mod = importlib.import_module(str(name))
        load_from_python_object(obj, mod, name, key, identifier)
        return True  # loaded ok!
    # if it reaches this point that means exception occurred, module not found.
    return False