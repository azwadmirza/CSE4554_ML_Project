def sum_parallel_impl(return_type, arg):
    zero = return_type(0)

    if arg.ndim == 0:
        def sum_1(in_arr):
            return in_arr[()]
    elif arg.ndim == 1:
        def sum_1(in_arr):
            numba.parfor.init_prange()
            val = zero
            for i in numba.parfor.internal_prange(len(in_arr)):
                val += in_arr[i]
            return val
    else:
        def sum_1(in_arr):
            numba.parfor.init_prange()
            val = zero
            for i in numba.pndindex(in_arr.shape):
                val += in_arr[i]
            return val
    return sum_1