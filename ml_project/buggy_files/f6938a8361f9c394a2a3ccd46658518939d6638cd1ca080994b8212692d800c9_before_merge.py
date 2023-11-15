def create_struct_proxy(fe_type):
    """
    Returns a specialized StructProxy subclass for the given fe_type.
    """
    res = _struct_proxy_cache.get(fe_type)
    if res is None:
        clsname = StructProxy.__name__ + '_' + str(fe_type)
        bases = (StructProxy,)
        clsmembers = dict(_fe_type=fe_type)
        res = type(clsname, bases, clsmembers)
        _struct_proxy_cache[fe_type] = res
    return res