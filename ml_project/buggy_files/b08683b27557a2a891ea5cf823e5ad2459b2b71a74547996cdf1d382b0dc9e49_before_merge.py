def init_dict(data: Dict, index, columns, dtype: Optional[DtypeObj] = None):
    """
    Segregate Series based on type and coerce into matrices.
    Needs to handle a lot of exceptional cases.
    """
    arrays: Union[Sequence[Any], "Series"]

    if columns is not None:
        from pandas.core.series import Series  # noqa:F811

        arrays = Series(data, index=columns, dtype=object)
        data_names = arrays.index

        missing = arrays.isna()
        if index is None:
            # GH10856
            # raise ValueError if only scalars in dict
            index = extract_index(arrays[~missing])
        else:
            index = ensure_index(index)

        # no obvious "empty" int column
        if missing.any() and not is_integer_dtype(dtype):
            if dtype is None or np.issubdtype(dtype, np.flexible):
                # GH#1783
                nan_dtype = np.dtype(object)
            else:
                nan_dtype = dtype
            val = construct_1d_arraylike_from_scalar(np.nan, len(index), nan_dtype)
            arrays.loc[missing] = [val] * missing.sum()

    else:
        keys = list(data.keys())
        columns = data_names = Index(keys)
        arrays = [com.maybe_iterable_to_list(data[k]) for k in keys]
        # GH#24096 need copy to be deep for datetime64tz case
        # TODO: See if we can avoid these copies
        arrays = [
            arr if not isinstance(arr, ABCIndexClass) else arr._data for arr in arrays
        ]
        arrays = [
            arr if not is_datetime64tz_dtype(arr) else arr.copy() for arr in arrays
        ]
    return arrays_to_mgr(arrays, data_names, index, columns, dtype=dtype)