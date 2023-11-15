def var_parallel_impl(return_type, arg):
    if arg.ndim == 0:
        def var_1(in_arr):
            return 0
    elif arg.ndim == 1:
        def var_1(in_arr):
            # Compute the mean
            m = in_arr.mean()
            # Compute the sum of square diffs
            numba.parfor.init_prange()
            ssd = 0
            for i in numba.parfor.internal_prange(len(in_arr)):
                val = in_arr[i] - m
                ssd += np.real(val * np.conj(val))
            return ssd / len(in_arr)
    else:
        def var_1(in_arr):
            # Compute the mean
            m = in_arr.mean()
            # Compute the sum of square diffs
            numba.parfor.init_prange()
            ssd = 0
            for i in numba.pndindex(in_arr.shape):
                val = in_arr[i] - m
                ssd += np.real(val * np.conj(val))
            return ssd / in_arr.size
    return var_1