def is_cython_func(func: Callable) -> bool:
    """Slightly hacky check for whether a callable is implemented in Cython.
    Can be used to implement slightly different behaviors, especially around
    inspecting and parameter annotations. Note that this will only return True
    for actual cdef functions and methods, not regular Python functions defined
    in Python modules.

    func (Callable): The callable to check.
    RETURNS (bool): Whether the callable is Cython (probably).
    """
    attr = "__pyx_vtable__"
    if hasattr(func, attr):  # function or class instance
        return True
    # https://stackoverflow.com/a/55767059
    if hasattr(func, "__qualname__") and hasattr(func, "__module__") \
        and func.__module__ in sys.modules:  # method
            cls_func = vars(sys.modules[func.__module__])[func.__qualname__.split(".")[0]]
            return hasattr(cls_func, attr)
    return False