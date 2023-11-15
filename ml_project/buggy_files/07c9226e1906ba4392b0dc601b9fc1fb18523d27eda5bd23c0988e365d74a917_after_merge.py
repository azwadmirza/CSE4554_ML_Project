def find_module_path_and_all_py3(module: str) -> Optional[Tuple[str, Optional[List[str]]]]:
    """Find module and determine __all__ for a Python 3 module.

    Return None if the module is a C module. Return (module_path, __all__) if
    it is a Python module. Raise CantImport if import failed.
    """
    # TODO: Support custom interpreters.
    try:
        mod = importlib.import_module(module)
    except Exception:
        raise CantImport(module)
    if is_c_module(mod):
        return None
    module_all = getattr(mod, '__all__', None)
    if module_all is not None:
        module_all = list(module_all)
    return mod.__file__, module_all