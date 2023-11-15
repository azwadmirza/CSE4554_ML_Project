def get_parfor_reductions(parfor):
    """get variables that are accumulated using inplace_binop inside the parfor
    and need to be passed as reduction parameters to gufunc.
    """
    last_label = max(parfor.loop_body.keys())
    reductions = {}
    names = []
    parfor_params = get_parfor_params(parfor)
    for blk in parfor.loop_body.values():
        for stmt in blk.body:
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr) and stmt.value.op == "inplace_binop":
                name = stmt.value.lhs.name
                if name in parfor_params:
                    names.append(name)
                    reductions[name] = (stmt.value.fn, stmt.value.immutable_fn)
    return sorted(names), reductions