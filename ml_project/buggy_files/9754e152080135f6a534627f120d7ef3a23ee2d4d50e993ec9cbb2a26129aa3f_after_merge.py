def ensure_dtype_not_object(var, name=None):
    # TODO: move this from conventions to backends? (it's not CF related)
    if var.dtype.kind == 'O':
        dims, data, attrs, encoding = _var_as_tuple(var)
        missing = pd.isnull(data)
        if missing.any():
            # nb. this will fail for dask.array data
            non_missing_values = data[~missing]
            inferred_dtype = _infer_dtype(non_missing_values, name)

            # There is no safe bit-pattern for NA in typical binary string
            # formats, we so can't set a fill_value. Unfortunately, this means
            # we can't distinguish between missing values and empty strings.
            if inferred_dtype.kind == 'S':
                fill_value = b''
            elif inferred_dtype.kind == 'U':
                fill_value = u''
            else:
                # insist on using float for numeric values
                if not np.issubdtype(inferred_dtype, float):
                    inferred_dtype = np.dtype(float)
                fill_value = inferred_dtype.type(np.nan)

            data = np.array(data, dtype=inferred_dtype, copy=True)
            data[missing] = fill_value
        else:
            data = data.astype(dtype=_infer_dtype(data, name))
        var = Variable(dims, data, attrs, encoding)
    return var