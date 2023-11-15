def _try_cast(
    arr, dtype: Optional[DtypeObj], copy: bool, raise_cast_failure: bool,
):
    """
    Convert input to numpy ndarray and optionally cast to a given dtype.

    Parameters
    ----------
    arr : ndarray, list, tuple, iterator (catchall)
        Excludes: ExtensionArray, Series, Index.
    dtype : np.dtype, ExtensionDtype or None
    copy : bool
        If False, don't copy the data if not needed.
    raise_cast_failure : bool
        If True, and if a dtype is specified, raise errors during casting.
        Otherwise an object array is returned.
    """
    # perf shortcut as this is the most common case
    if isinstance(arr, np.ndarray):
        if maybe_castable(arr) and not copy and dtype is None:
            return arr

    if isinstance(dtype, ExtensionDtype) and dtype.kind != "M":
        # create an extension array from its dtype
        # DatetimeTZ case needs to go through maybe_cast_to_datetime
        array_type = dtype.construct_array_type()._from_sequence
        subarr = array_type(arr, dtype=dtype, copy=copy)
        return subarr

    try:
        # GH#15832: Check if we are requesting a numeric dype and
        # that we can convert the data to the requested dtype.
        if is_integer_dtype(dtype):
            # this will raise if we have e.g. floats
            maybe_cast_to_integer_array(arr, dtype)
            subarr = arr
        else:
            subarr = maybe_cast_to_datetime(arr, dtype)

        # Take care in creating object arrays (but iterators are not
        # supported):
        if is_object_dtype(dtype) and (
            is_list_like(subarr)
            and not (is_iterator(subarr) or isinstance(subarr, np.ndarray))
        ):
            subarr = construct_1d_object_array_from_listlike(subarr)
        elif not is_extension_array_dtype(subarr):
            subarr = construct_1d_ndarray_preserving_na(subarr, dtype, copy=copy)
    except OutOfBoundsDatetime:
        # in case of out of bound datetime64 -> always raise
        raise
    except (ValueError, TypeError):
        if dtype is not None and raise_cast_failure:
            raise
        else:
            subarr = np.array(arr, dtype=object, copy=copy)
    return subarr