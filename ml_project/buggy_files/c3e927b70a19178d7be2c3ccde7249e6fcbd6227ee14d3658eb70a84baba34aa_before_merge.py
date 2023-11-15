def mean_parallel_impl(return_type, arg):
    # can't reuse sum since output type is different
    zero = return_type(0)

    if arg.ndim == 1:
        def mean_1(in_arr):
            numba.parfor.init_prange()
            val = zero
            for i in numba.parfor.internal_prange(len(in_arr)):
                val += in_arr[i]
            return val/len(in_arr)
    else:
        def mean_1(in_arr):
            numba.parfor.init_prange()
            val = zero
            for i in numba.pndindex(in_arr.shape):
                val += in_arr[i]
            return val/in_arr.size
    return mean_1