def ensure_dtype_not_object(var, name=None):
    # TODO: move this from conventions to backends? (it's not CF related)
    if var.dtype.kind == 'O':
        dims, data, attrs, encoding = _var_as_tuple(var)

        if isinstance(data, dask_array_type):
            warnings.warn(
                'variable {} has data in the form of a dask array with '
                'dtype=object, which means it is being loaded into memory '
                'to determine a data type that can be safely stored on disk. '
                'To avoid this, coerce this variable to a fixed-size dtype '
                'with astype() before saving it.'.format(name),
                SerializationWarning)
            data = data.compute()

        missing = pd.isnull(data)
        if missing.any():
            # nb. this will fail for dask.array data
            non_missing_values = data[~missing]
            inferred_dtype = _infer_dtype(non_missing_values, name)

            # There is no safe bit-pattern for NA in typical binary string
            # formats, we so can't set a fill_value. Unfortunately, this means
            # we can't distinguish between missing values and empty strings.
            if strings.is_bytes_dtype(inferred_dtype):
                fill_value = b''
            elif strings.is_unicode_dtype(inferred_dtype):
                fill_value = u''
            else:
                # insist on using float for numeric values
                if not np.issubdtype(inferred_dtype, np.floating):
                    inferred_dtype = np.dtype(float)
                fill_value = inferred_dtype.type(np.nan)

            data = _copy_with_dtype(data, dtype=inferred_dtype)
            data[missing] = fill_value
        else:
            data = _copy_with_dtype(data, dtype=_infer_dtype(data, name))

        assert data.dtype.kind != 'O' or data.dtype.metadata
        var = Variable(dims, data, attrs, encoding)
    return var