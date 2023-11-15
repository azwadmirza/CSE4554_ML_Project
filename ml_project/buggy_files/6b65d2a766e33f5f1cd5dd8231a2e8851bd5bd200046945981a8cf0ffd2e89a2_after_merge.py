def get_parfor_reductions(parfor, parfor_params, reductions=None, names=None):
    """get variables that are accumulated using inplace_binop inside the parfor
    and need to be passed as reduction parameters to gufunc.
    """
    if reductions is None:
        reductions = {}
    if names is None:
        names = []
    last_label = max(parfor.loop_body.keys())

    for blk in parfor.loop_body.values():
        for stmt in blk.body:
            if (isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr)
                    and stmt.value.op == "inplace_binop"):
                name = stmt.value.lhs.name
                if name in parfor_params:
                    names.append(name)
                    red_info = None
                    for (acc_op, imm_op, init_val) in _reduction_ops.values():
                        if imm_op == stmt.value.immutable_fn:
                            red_info = (
                                stmt.value.fn, stmt.value.immutable_fn, init_val)
                            break
                    if red_info is None:
                        raise NotImplementedError(
                            "Reduction is not support for inplace operator %s" %
                            stmt.value.fn)
                    reductions[name] = red_info
            if isinstance(stmt, Parfor):
                # recursive parfors can have reductions like test_prange8
                get_parfor_reductions(stmt, parfor_params, reductions, names)
    return names, reductions