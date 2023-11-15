def maybe_casted_values(index, codes=None):
    """
    Convert an index, given directly or as a pair (level, code), to a 1D array.

    Parameters
    ----------
    index : Index
    codes : sequence of integers (optional)

    Returns
    -------
    ExtensionArray or ndarray
        If codes is `None`, the values of `index`.
        If codes is passed, an array obtained by taking from `index` the indices
        contained in `codes`.
    """

    values = index._values
    if not isinstance(index, (ABCPeriodIndex, ABCDatetimeIndex)):
        if values.dtype == np.object_:
            values = lib.maybe_convert_objects(values)

    # if we have the codes, extract the values with a mask
    if codes is not None:
        mask = codes == -1

        # we can have situations where the whole mask is -1,
        # meaning there is nothing found in codes, so make all nan's
        if mask.size > 0 and mask.all():
            dtype = index.dtype
            fill_value = na_value_for_dtype(dtype)
            values = construct_1d_arraylike_from_scalar(fill_value, len(mask), dtype)
        else:
            values = values.take(codes)

            # TODO(https://github.com/pandas-dev/pandas/issues/24206)
            # Push this into maybe_upcast_putmask?
            # We can't pass EAs there right now. Looks a bit
            # complicated.
            # So we unbox the ndarray_values, op, re-box.
            values_type = type(values)
            values_dtype = values.dtype

            from pandas.core.arrays.datetimelike import DatetimeLikeArrayMixin

            if isinstance(values, DatetimeLikeArrayMixin):
                values = values._data  # TODO: can we de-kludge yet?

            if mask.any():
                values, _ = maybe_upcast_putmask(values, mask, np.nan)

            if issubclass(values_type, DatetimeLikeArrayMixin):
                values = values_type(values, dtype=values_dtype)

    return values