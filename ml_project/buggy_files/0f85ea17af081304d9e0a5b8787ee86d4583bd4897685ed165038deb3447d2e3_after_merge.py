def _is_list_like(obj):
    # Consider namedtuples to be not list like as they are useful as indices
    return (np.iterable(obj)
            and not isinstance(obj, basestring)
            and not (isinstance(obj, tuple) and type(obj) is not tuple))