def _sanitize_array(data, index, dtype=None, copy=False,
                    raise_cast_failure=False):
    """ sanitize input data to an ndarray, copy if specified, coerce to the
    dtype if specified
    """

    if dtype is not None:
        dtype = pandas_dtype(dtype)

    if isinstance(data, ma.MaskedArray):
        mask = ma.getmaskarray(data)
        if mask.any():
            data, fill_value = maybe_upcast(data, copy=True)
            data[mask] = fill_value
        else:
            data = data.copy()

    def _try_cast(arr, take_fast_path):

        # perf shortcut as this is the most common case
        if take_fast_path:
            if maybe_castable(arr) and not copy and dtype is None:
                return arr

        try:
            subarr = maybe_cast_to_datetime(arr, dtype)
            if not is_extension_type(subarr):
                subarr = np.array(subarr, dtype=dtype, copy=copy)
        except (ValueError, TypeError):
            if is_categorical_dtype(dtype):
                # We *do* allow casting to categorical, since we know
                # that Categorical is the only array type for 'category'.
                subarr = Categorical(arr, dtype.categories,
                                     ordered=dtype.ordered)
            elif is_extension_array_dtype(dtype):
                # We don't allow casting to third party dtypes, since we don't
                # know what array belongs to which type.
                msg = ("Cannot cast data to extension dtype '{}'. "
                       "Pass the extension array directly.".format(dtype))
                raise ValueError(msg)

            elif dtype is not None and raise_cast_failure:
                raise
            else:
                subarr = np.array(arr, dtype=object, copy=copy)
        return subarr

    # GH #846
    if isinstance(data, (np.ndarray, Index, Series)):

        if dtype is not None:
            subarr = np.array(data, copy=False)

            # possibility of nan -> garbage
            if is_float_dtype(data.dtype) and is_integer_dtype(dtype):
                if not isna(data).any():
                    subarr = _try_cast(data, True)
                elif copy:
                    subarr = data.copy()
            else:
                subarr = _try_cast(data, True)
        elif isinstance(data, Index):
            # don't coerce Index types
            # e.g. indexes can have different conversions (so don't fast path
            # them)
            # GH 6140
            subarr = _sanitize_index(data, index, copy=copy)
        else:

            # we will try to copy be-definition here
            subarr = _try_cast(data, True)

    elif isinstance(data, ExtensionArray):
        subarr = data

        if dtype is not None and not data.dtype.is_dtype(dtype):
            msg = ("Cannot coerce extension array to dtype '{typ}'. "
                   "Do the coercion before passing to the constructor "
                   "instead.".format(typ=dtype))
            raise ValueError(msg)

        if copy:
            subarr = data.copy()
        return subarr

    elif isinstance(data, (list, tuple)) and len(data) > 0:
        if dtype is not None:
            try:
                subarr = _try_cast(data, False)
            except Exception:
                if raise_cast_failure:  # pragma: no cover
                    raise
                subarr = np.array(data, dtype=object, copy=copy)
                subarr = lib.maybe_convert_objects(subarr)

        else:
            subarr = maybe_convert_platform(data)

        subarr = maybe_cast_to_datetime(subarr, dtype)

    elif isinstance(data, range):
        # GH 16804
        start, stop, step = get_range_parameters(data)
        arr = np.arange(start, stop, step, dtype='int64')
        subarr = _try_cast(arr, False)
    else:
        subarr = _try_cast(data, False)

    # scalar like, GH
    if getattr(subarr, 'ndim', 0) == 0:
        if isinstance(data, list):  # pragma: no cover
            subarr = np.array(data, dtype=object)
        elif index is not None:
            value = data

            # figure out the dtype from the value (upcast if necessary)
            if dtype is None:
                dtype, value = infer_dtype_from_scalar(value)
            else:
                # need to possibly convert the value here
                value = maybe_cast_to_datetime(value, dtype)

            subarr = construct_1d_arraylike_from_scalar(
                value, len(index), dtype)

        else:
            return subarr.item()

    # the result that we want
    elif subarr.ndim == 1:
        if index is not None:

            # a 1-element ndarray
            if len(subarr) != len(index) and len(subarr) == 1:
                subarr = construct_1d_arraylike_from_scalar(
                    subarr[0], len(index), subarr.dtype)

    elif subarr.ndim > 1:
        if isinstance(data, np.ndarray):
            raise Exception('Data must be 1-dimensional')
        else:
            subarr = com._asarray_tuplesafe(data, dtype=dtype)

    # This is to prevent mixed-type Series getting all casted to
    # NumPy string type, e.g. NaN --> '-1#IND'.
    if issubclass(subarr.dtype.type, compat.string_types):
        # GH 16605
        # If not empty convert the data to dtype
        # GH 19853: If data is a scalar, subarr has already the result
        if not is_scalar(data):
            if not np.all(isna(data)):
                data = np.array(data, dtype=dtype, copy=False)
            subarr = np.array(data, dtype=object, copy=copy)

    return subarr