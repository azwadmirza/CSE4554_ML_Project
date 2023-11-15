def _has_bool_dtype(x):
    try:
        if isinstance(x, ABCDataFrame):
            return 'bool' in x.dtypes
        else:
            return x.dtype == bool
    except AttributeError:
        return isinstance(x, (bool, np.bool_))