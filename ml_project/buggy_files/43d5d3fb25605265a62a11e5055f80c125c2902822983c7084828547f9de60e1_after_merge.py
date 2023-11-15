def _stack_dict(dct, ref_items, dtype):
    from pandas.core.series import Series

    # fml
    def _asarray_compat(x):
        # asarray shouldn't be called on SparseSeries
        if isinstance(x, Series):
            return x.values
        else:
            return np.asarray(x)

    def _shape_compat(x):
        # sparseseries
        if isinstance(x, Series):
            return len(x),
        else:
            return x.shape

    # index may box values
    items = ref_items[[x in dct for x in ref_items]]

    first = dct[items[0]]
    shape = (len(dct),) + _shape_compat(first)

    stacked = np.empty(shape, dtype=dtype)
    for i, item in enumerate(items):
        stacked[i] = _asarray_compat(dct[item])

    # stacked = np.vstack([_asarray_compat(dct[k]) for k in items])
    return items, stacked