def _arange_dtype(*args):
    bounds = [a for a in args if not isinstance(a, types.NoneType)]

    if any(isinstance(a, types.Complex) for a in bounds):
        dtype = types.complex128
    elif any(isinstance(a, types.Float) for a in bounds):
        dtype = types.float64
    else:
        # numerous attempts were made at guessing this type from the NumPy
        # source but it turns out on running `np.arange(10).dtype` on pretty
        # much all platform and python combinations that it matched np.int?!
        # Windows 64 is broken by default here because Numba (as of 0.47) does
        # not differentiate between Python and NumPy integers, so a `typeof(1)`
        # on w64 is `int64`, i.e. `intp`. This means an arange(<some int>) will
        # be typed as arange(int64) and the following will yield int64 opposed
        # to int32. Example: without a load of analysis to work out of the args
        # were wrapped in NumPy int*() calls it's not possible to detect the
        # difference between `np.arange(10)` and `np.arange(np.int64(10)`.
        NPY_TY = getattr(types, "int%s" % (8 * np.dtype(np.int).itemsize))
        dtype = max(bounds + [NPY_TY,])

    return dtype