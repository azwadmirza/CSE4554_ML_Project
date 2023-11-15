def prod_parallel_impl(return_type, arg):
    one = return_type(1)

    if arg.ndim == 1:
        def prod_1(in_arr):
            numba.parfor.init_prange()
            val = one
            for i in numba.parfor.internal_prange(len(in_arr)):
                val *= in_arr[i]
            return val
    else:
        def prod_1(in_arr):
            numba.parfor.init_prange()
            val = one
            for i in numba.pndindex(in_arr.shape):
                val *= in_arr[i]
            return val
    return prod_1