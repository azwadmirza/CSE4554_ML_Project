def has_no_side_effect(rhs, lives, call_table):
    """ Returns True if this expression has no side effects that
        would prevent re-ordering.
    """
    if isinstance(rhs, ir.Expr) and rhs.op == 'call':
        func_name = rhs.func.name
        if func_name not in call_table or call_table[func_name] == []:
            return False
        call_list = call_table[func_name]
        if (call_list == ['empty', numpy] or
            call_list == [slice] or
            call_list == ['stencil', numba] or
            call_list == ['log', numpy] or
            call_list == [numba.array_analysis.wrap_index]):
            return True
        elif (isinstance(call_list[0], numba.extending._Intrinsic) and
              (call_list[0]._name == 'empty_inferred' or
               call_list[0]._name == 'unsafe_empty_inferred')):
            return True
        from numba.targets.registry import CPUDispatcher
        from numba.targets.linalg import dot_3_mv_check_args
        if isinstance(call_list[0], CPUDispatcher):
            py_func = call_list[0].py_func
            if py_func == dot_3_mv_check_args:
                return True
        for f in remove_call_handlers:
            if f(rhs, lives, call_list):
                return True
        return False
    if isinstance(rhs, ir.Expr) and rhs.op == 'inplace_binop':
        return rhs.lhs.name not in lives
    if isinstance(rhs, ir.Yield):
        return False
    if isinstance(rhs, ir.Expr) and rhs.op == 'pair_first':
        # don't remove pair_first since prange looks for it
        return False
    return True