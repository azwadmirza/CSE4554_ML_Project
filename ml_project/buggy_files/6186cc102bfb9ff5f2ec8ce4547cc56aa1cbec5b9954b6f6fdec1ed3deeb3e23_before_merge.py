def encode_cf_variable(var, needs_copy=True, name=None):
    """
    Converts an Variable into an Variable which follows some
    of the CF conventions:

        - Nans are masked using _FillValue (or the deprecated missing_value)
        - Rescaling via: scale_factor and add_offset
        - datetimes are converted to the CF 'units since time' format
        - dtype encodings are enforced.

    Parameters
    ----------
    var : xarray.Variable
        A variable holding un-encoded data.

    Returns
    -------
    out : xarray.Variable
        A variable which has been encoded as described above.
    """
    var = maybe_encode_datetime(var, name=name)
    var = maybe_encode_timedelta(var, name=name)
    var, needs_copy = maybe_encode_offset_and_scale(var, needs_copy, name=name)
    var, needs_copy = maybe_encode_fill_value(var, needs_copy, name=name)
    var = maybe_encode_nonstring_dtype(var, name=name)
    var = maybe_default_fill_value(var)
    var = maybe_encode_bools(var)
    var = ensure_dtype_not_object(var, name=name)
    var = maybe_encode_string_dtype(var, name=name)
    return var