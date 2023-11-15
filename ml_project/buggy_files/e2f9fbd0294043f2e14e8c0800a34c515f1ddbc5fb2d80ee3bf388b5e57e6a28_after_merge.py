def _get_empty_meta(columns, index_col, index_names, dtype=None):
    columns = list(columns)

    # Convert `dtype` to a defaultdict of some kind.
    # This will enable us to write `dtype[col_name]`
    # without worrying about KeyError issues later on.
    if not isinstance(dtype, dict):
        # if dtype == None, default will be np.object.
        default_dtype = dtype or np.object
        dtype = defaultdict(lambda: default_dtype)
    else:
        # Save a copy of the dictionary.
        _dtype = dtype.copy()
        dtype = defaultdict(lambda: np.object)

        # Convert column indexes to column names.
        for k, v in compat.iteritems(_dtype):
            col = columns[k] if is_integer(k) else k
            dtype[col] = v

    # Even though we have no data, the "index" of the empty DataFrame
    # could for example still be an empty MultiIndex. Thus, we need to
    # check whether we have any index columns specified, via either:
    #
    # 1) index_col (column indices)
    # 2) index_names (column names)
    #
    # Both must be non-null to ensure a successful construction. Otherwise,
    # we have to create a generic emtpy Index.
    if (index_col is None or index_col is False) or index_names is None:
        index = Index([])
    else:
        data = [Series([], dtype=dtype[name]) for name in index_names]
        index = _ensure_index_from_sequences(data, names=index_names)
        index_col.sort()

        for i, n in enumerate(index_col):
            columns.pop(n - i)

    col_dict = {col_name: Series([], dtype=dtype[col_name])
                for col_name in columns}

    return index, columns, col_dict