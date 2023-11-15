def _reduce_function(func, globs):
    """
    Reduce a Python function and its globals to picklable components.
    If there are cell variables (i.e. references to a closure), their
    values will be frozen.
    """
    if func.__closure__:
        cells = [cell.cell_contents for cell in func.__closure__]
    else:
        cells = None
    return _reduce_code(func.__code__), globs, func.__name__, cells, func.__defaults__