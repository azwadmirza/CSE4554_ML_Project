def _arange_dtype(*args):
    bounds = [a for a in args if not isinstance(a, types.NoneType)]

    if any(isinstance(a, types.Complex) for a in bounds):
        dtype = types.complex128
    elif any(isinstance(a, types.Float) for a in bounds):
        dtype = types.float64
    else:
        # It's not possible for the dtype to replicate NumPy as integer literals
        # are intp size in Numba but np.dtype(int) (i.e. intc) in NumPy. The
        # NumPy logic is to basically do max(np.long, *[type(x) for x in args]).
        # On windows 64, in NumPy, that would mean:
        # * np.arange(1, 10) -> max(np.long, np.intc, np.intc) -> int32
        # but in Numba:
        # * np.arange(1, 10) -> max(np.long, np.intp, np.intp) -> int64
        #
        # It's therefore not possible to replicate the case where integer
        # literals are supplied, however best effort is made to correctly handle
        # cases like:
        # * np.arange(np.int8(10)) -> max(np.long, np.int8) -> np.long
        #
        # Alg ref:
        # https://github.com/numpy/numpy/blob/maintenance/1.17.x/numpy/core/src/multiarray/ctors.c#L3376-L3377    # noqa: E501
        #
        # Also not Py2.7 on 32 bit linux as a 32bit np.long where as Py3 has a
        # 64bit, numba is not replicating this!
        dtype = max(bounds + [types.long_,])

    return dtype