def argmax_parallel_impl(in_arr):
    numba.parfor.init_prange()
    argmax_checker(len(in_arr))
    A = in_arr.ravel()
    init_val = numba.targets.builtins.get_type_min_value(A.dtype)
    ival = numba.typing.builtins.IndexValue(0, init_val)
    for i in numba.parfor.internal_prange(len(A)):
        curr_ival = numba.typing.builtins.IndexValue(i, A[i])
        ival = max(ival, curr_ival)
    return ival.index