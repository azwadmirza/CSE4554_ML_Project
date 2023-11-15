def _sanitize_array(data, index, dtype=None, copy=False,
                    raise_cast_failure=False):
    """ sanitize input data to an ndarray, copy if specified, coerce to the
    dtype if specified
    """

    if dtype is not None:
        dtype = _coerce_to_dtype(dtype)

    if isinstance(data, ma.MaskedArray):
        mask = ma.getmaskarray(data)
        if mask.any():
            data, fill_value = _maybe_upcast(data, copy=True)
            data[mask] = fill_value
        else:
            data = data.copy()

    def _try_cast(arr, take_fast_path):

        # perf shortcut as this is the most common case
        if take_fast_path:
            if _possibly_castable(arr) and not copy and dtype is None:
                return arr

        try:
            subarr = _possibly_cast_to_datetime(arr, dtype)
            if not is_extension_type(subarr):
                subarr = np.array(subarr, dtype=dtype, copy=copy)
        except (ValueError, TypeError):
            if is_categorical_dtype(dtype):
                subarr = Categorical(arr)
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
                if not isnull(data).any():
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
            subarr = _sanitize_index(data, index, copy=True)
        else:
            subarr = _try_cast(data, True)

        if copy:
            subarr = data.copy()

    elif isinstance(data, Categorical):
        subarr = data

        if copy:
            subarr = data.copy()
        return subarr

    elif isinstance(data, list) and len(data) > 0:
        if dtype is not None:
            try:
                subarr = _try_cast(data, False)
            except Exception:
                if raise_cast_failure:  # pragma: no cover
                    raise
                subarr = np.array(data, dtype=object, copy=copy)
                subarr = lib.maybe_convert_objects(subarr)

        else:
            subarr = _possibly_convert_platform(data)

        subarr = _possibly_cast_to_datetime(subarr, dtype)

    else:
        subarr = _try_cast(data, False)

    def create_from_value(value, index, dtype):
        # return a new empty value suitable for the dtype

        if is_datetimetz(dtype):
            subarr = DatetimeIndex([value] * len(index), dtype=dtype)
        elif is_categorical_dtype(dtype):
            subarr = Categorical([value] * len(index))
        else:
            if not isinstance(dtype, (np.dtype, type(np.dtype))):
                dtype = dtype.dtype
            subarr = np.empty(len(index), dtype=dtype)
            subarr.fill(value)

        return subarr

    # scalar like
    if subarr.ndim == 0:
        if isinstance(data, list):  # pragma: no cover
            subarr = np.array(data, dtype=object)
        elif index is not None:
            value = data

            # figure out the dtype from the value (upcast if necessary)
            if dtype is None:
                dtype, value = _infer_dtype_from_scalar(value)
            else:
                # need to possibly convert the value here
                value = _possibly_cast_to_datetime(value, dtype)

            subarr = create_from_value(value, index, dtype)

        else:
            return subarr.item()

    # the result that we want
    elif subarr.ndim == 1:
        if index is not None:

            # a 1-element ndarray
            if len(subarr) != len(index) and len(subarr) == 1:
                subarr = create_from_value(subarr[0], index,
                                           subarr.dtype)

    elif subarr.ndim > 1:
        if isinstance(data, np.ndarray):
            raise Exception('Data must be 1-dimensional')
        else:
            subarr = _asarray_tuplesafe(data, dtype=dtype)

    # This is to prevent mixed-type Series getting all casted to
    # NumPy string type, e.g. NaN --> '-1#IND'.
    if issubclass(subarr.dtype.type, compat.string_types):
        subarr = np.array(data, dtype=object, copy=copy)

    return subarr