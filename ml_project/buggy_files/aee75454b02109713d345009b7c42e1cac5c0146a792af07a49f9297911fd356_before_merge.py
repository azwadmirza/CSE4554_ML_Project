def min_parallel_impl(return_type, arg):
    # XXX: use prange for 1D arrays since pndindex returns a 1-tuple instead of
    # integer. This causes type and fusion issues.
    if arg.ndim == 1:
        def min_1(in_arr):
            numba.parfor.init_prange()
            min_checker(len(in_arr))
            val = numba.targets.builtins.get_type_max_value(in_arr.dtype)
            for i in numba.parfor.internal_prange(len(in_arr)):
                val = min(val, in_arr[i])
            return val
    else:
        def min_1(in_arr):
            numba.parfor.init_prange()
            min_checker(len(in_arr))
            val = numba.targets.builtins.get_type_max_value(in_arr.dtype)
            for i in numba.pndindex(in_arr.shape):
                val = min(val, in_arr[i])
            return val
    return min_1