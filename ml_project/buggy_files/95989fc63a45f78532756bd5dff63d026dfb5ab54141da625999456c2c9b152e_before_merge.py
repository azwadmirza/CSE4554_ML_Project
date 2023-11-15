def _has_bool_dtype(x):
    try:
        return x.dtype == bool
    except AttributeError:
        try:
            return 'bool' in x.dtypes
        except AttributeError:
            return isinstance(x, (bool, np.bool_))