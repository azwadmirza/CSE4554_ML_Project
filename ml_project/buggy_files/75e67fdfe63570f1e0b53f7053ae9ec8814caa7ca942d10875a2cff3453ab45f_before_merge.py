def get_parfor_reductions(parfor, parfor_params, calltypes, reductions=None,
        reduce_varnames=None, param_uses=None, param_nodes=None,
        var_to_param=None):
    """find variables that are updated using their previous values and an array
    item accessed with parfor index, e.g. s = s+A[i]
    """
    if reductions is None:
        reductions = {}
    if reduce_varnames is None:
        reduce_varnames = []

    # for each param variable, find what other variables are used to update it
    # also, keep the related nodes
    if param_uses is None:
        param_uses = defaultdict(list)
    if param_nodes is None:
        param_nodes = defaultdict(list)
    if var_to_param is None:
        var_to_param = {}

    blocks = wrap_parfor_blocks(parfor)
    topo_order = find_topo_order(blocks)
    topo_order = topo_order[1:]  # ignore init block
    unwrap_parfor_blocks(parfor)

    for label in reversed(topo_order):
        for stmt in reversed(parfor.loop_body[label].body):
            if (isinstance(stmt, ir.Assign)
                    and (stmt.target.name in parfor_params
                        or stmt.target.name in var_to_param)):
                lhs = stmt.target.name
                rhs = stmt.value
                cur_param = lhs if lhs in parfor_params else var_to_param[lhs]
                used_vars = []
                if isinstance(rhs, ir.Var):
                    used_vars = [rhs.name]
                elif isinstance(rhs, ir.Expr):
                    used_vars = [v.name for v in stmt.value.list_vars()]
                param_uses[cur_param].extend(used_vars)
                for v in used_vars:
                    var_to_param[v] = cur_param
                # save copy of dependent stmt
                stmt_cp = copy.deepcopy(stmt)
                if stmt.value in calltypes:
                    calltypes[stmt_cp.value] = calltypes[stmt.value]
                param_nodes[cur_param].append(stmt_cp)
            if isinstance(stmt, Parfor):
                # recursive parfors can have reductions like test_prange8
                get_parfor_reductions(stmt, parfor_params, calltypes,
                    reductions, reduce_varnames, param_uses, param_nodes, var_to_param)
    for param, used_vars in param_uses.items():
        # a parameter is a reduction variable if its value is used to update it
        # check reduce_varnames since recursive parfors might have processed
        # param already
        if param in used_vars and param not in reduce_varnames:
            reduce_varnames.append(param)
            param_nodes[param].reverse()
            reduce_nodes = get_reduce_nodes(param, param_nodes[param])
            gri_out = guard(get_reduction_init, reduce_nodes)
            if gri_out is not None:
                init_val, redop = gri_out
            else:
                init_val = None
                redop = None
            reductions[param] = (init_val, reduce_nodes, redop)
    return reduce_varnames, reductions