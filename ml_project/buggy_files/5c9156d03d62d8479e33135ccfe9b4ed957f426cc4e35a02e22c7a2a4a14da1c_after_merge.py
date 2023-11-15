def argmin_parallel_impl(in_arr):
    numba.parfor.init_prange()
    argmin_checker(len(in_arr))
    A = in_arr.ravel()
    init_val = numba.targets.builtins.get_type_max_value(A.dtype)
    ival = numba.typing.builtins.IndexValue(0, init_val)
    for i in numba.parfor.internal_prange(len(A)):
        curr_ival = numba.typing.builtins.IndexValue(i, A[i])
        ival = min(ival, curr_ival)
    return ival.index