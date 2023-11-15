def create_struct_proxy(fe_type, kind='value'):
    """
    Returns a specialized StructProxy subclass for the given fe_type.
    """
    cache_key = (fe_type, kind)
    res = _struct_proxy_cache.get(cache_key)
    if res is None:
        base = {'value': ValueStructProxy,
                'data': DataStructProxy,
                }[kind]
        clsname = base.__name__ + '_' + str(fe_type)
        bases = (base,)
        clsmembers = dict(_fe_type=fe_type)
        res = type(clsname, bases, clsmembers)

        _struct_proxy_cache[cache_key] = res
    return res