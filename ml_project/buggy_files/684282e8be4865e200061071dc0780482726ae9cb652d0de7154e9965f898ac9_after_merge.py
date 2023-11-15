def count(values, uniques=None):
    f = lambda htype, caster: _count_generic(values, htype, caster)

    if uniques is not None:
        raise NotImplementedError
    else:
        return _hashtable_algo(f, values.dtype)