def has_no_side_effect(rhs, lives, call_table):
    # TODO: find side-effect free calls like Numpy calls
    if isinstance(rhs, ir.Expr) and rhs.op=='call':
        func_name = rhs.func.name
        if func_name not in call_table:
            return False
        call_list = call_table[func_name]
        if call_list==['empty', numpy] or call_list==[slice]:
            return True
        return False
    if isinstance(rhs, ir.Expr) and rhs.op=='inplace_binop':
        return rhs.lhs.name not in lives
    if isinstance(rhs, ir.Yield):
        return False
    return True