def _is_list_like(obj):
    return np.iterable(obj) and not isinstance(obj, basestring)