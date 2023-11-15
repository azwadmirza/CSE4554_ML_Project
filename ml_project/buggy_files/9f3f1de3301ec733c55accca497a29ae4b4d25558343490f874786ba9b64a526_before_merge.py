def _rebuild_function(code_reduced, globals, name, cell_values):
    """
    Rebuild a function from its _reduce_function() results.
    """
    if cell_values:
        cells = tuple(_dummy_closure(v).__closure__[0] for v in cell_values)
    else:
        cells = ()
    code = _rebuild_code(*code_reduced)
    modname = globals['__name__']
    try:
        _rebuild_module(modname)
    except ImportError:
        # If the module can't be found, avoid passing it (it would produce
        # errors when lowering).
        del globals['__name__']
    return FunctionType(code, globals, name, (), cells)