def get_name_from_func(func):
    # partials don't have `__module__` or `__name__`, so we use the values from the "inner" function
    if isinstance(func, partial_types):
        return "partial({})".format(get_name_from_func(func.func))
    elif hasattr(func, "_partialmethod") and hasattr(func._partialmethod, "func"):
        return "partial({})".format(get_name_from_func(func._partialmethod.func))

    module = func.__module__

    if hasattr(func, "__name__"):
        view_name = func.__name__
    else:  # Fall back if there's no __name__
        view_name = func.__class__.__name__

    return "{0}.{1}".format(module, view_name)