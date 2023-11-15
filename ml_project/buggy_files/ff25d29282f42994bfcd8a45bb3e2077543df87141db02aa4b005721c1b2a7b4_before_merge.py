def encode_zarr_variable(var, needs_copy=True, name=None):
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

    if var.dtype.kind == 'O':
        raise NotImplementedError("Variable `%s` is an object. Zarr "
                                  "store can't yet encode objects." % name)

    for coder in [coding.times.CFDatetimeCoder(),
                  coding.times.CFTimedeltaCoder(),
                  coding.variables.CFScaleOffsetCoder(),
                  coding.variables.CFMaskCoder(),
                  coding.variables.UnsignedIntegerCoder()]:
        var = coder.encode(var, name=name)

    var = conventions.maybe_encode_nonstring_dtype(var, name=name)
    var = conventions.maybe_default_fill_value(var)
    var = conventions.maybe_encode_bools(var)
    var = conventions.ensure_dtype_not_object(var, name=name)
    var = conventions.maybe_encode_string_dtype(var, name=name)
    return var