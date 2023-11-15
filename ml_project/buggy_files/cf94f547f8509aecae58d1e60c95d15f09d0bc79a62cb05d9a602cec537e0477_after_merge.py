def get_reduce_nodes(name, nodes, func_ir):
    """
    Get nodes that combine the reduction variable with a sentinel variable.
    Recognizes the first node that combines the reduction variable with another
    variable.
    """
    reduce_nodes = None
    defs = {}

    def lookup(var, varonly=True):
        val = defs.get(var.name, None)
        if isinstance(val, ir.Var):
            return lookup(val)
        else:
            return var if (varonly or val == None) else val

    for i, stmt in enumerate(nodes):
        lhs = stmt.target
        rhs = stmt.value
        defs[lhs.name] = rhs
        if isinstance(rhs, ir.Var) and rhs.name in defs:
            rhs = lookup(rhs)
        if isinstance(rhs, ir.Expr):
            in_vars = set(lookup(v, True).name for v in rhs.list_vars())
            if name in in_vars:
                next_node = nodes[i+1]
                if not (isinstance(next_node, ir.Assign) and next_node.target.name == name):
                    raise ValueError(("Use of reduction variable " + name +
                                      " other than in a supported reduction"
                                      " function is not permitted."))

                if not supported_reduction(rhs, func_ir):
                    raise ValueError(("Use of reduction variable " + name +
                                      " in an unsupported reduction function."))
                args = [ (x.name, lookup(x, True)) for x in get_expr_args(rhs) ]
                non_red_args = [ x for (x, y) in args if y.name != name ]
                assert len(non_red_args) == 1
                args = [ (x, y) for (x, y) in args if x != y.name ]
                replace_dict = dict(args)
                replace_dict[non_red_args[0]] = ir.Var(lhs.scope, name+"#init", lhs.loc)
                replace_vars_inner(rhs, replace_dict)
                reduce_nodes = nodes[i:]
                break;
    assert reduce_nodes, "Invalid reduction format"
    return reduce_nodes