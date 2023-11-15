        def min_1(in_arr):
            numba.parfor.init_prange()
            val = numba.targets.builtins.get_type_max_value(in_arr.dtype)
            for i in numba.pndindex(in_arr.shape):
                val = min(val, in_arr[i])
            return val