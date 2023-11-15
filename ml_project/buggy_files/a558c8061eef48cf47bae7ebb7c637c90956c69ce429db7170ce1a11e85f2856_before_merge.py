def max_parallel_impl(return_type, arg):
    if arg.ndim == 1:
        def max_1(in_arr):
            numba.parfor.init_prange()
            val = numba.targets.builtins.get_type_min_value(in_arr.dtype)
            for i in numba.parfor.internal_prange(len(in_arr)):
                val = max(val, in_arr[i])
            return val
    else:
        def max_1(in_arr):
            numba.parfor.init_prange()
            val = numba.targets.builtins.get_type_min_value(in_arr.dtype)
            for i in numba.pndindex(in_arr.shape):
                val = max(val, in_arr[i])
            return val
    return max_1