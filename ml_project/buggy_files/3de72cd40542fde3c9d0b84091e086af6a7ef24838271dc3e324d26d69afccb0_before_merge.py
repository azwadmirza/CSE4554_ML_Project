def visit_vars_inner(node, callback, cbdata):
    if isinstance(node, ir.Var):
        return callback(node, cbdata)
    elif isinstance(node, list):
        return [visit_vars_inner(n, callback, cbdata) for n in node]
    elif isinstance(node, tuple):
        return tuple([visit_vars_inner(n, callback, cbdata) for n in node])
    elif isinstance(node, ir.Expr):
        # if node.op in ['binop', 'inplace_binop']:
        #     lhs = node.lhs.name
        #     rhs = node.rhs.name
        #     node.lhs.name = callback, cbdata.get(lhs, lhs)
        #     node.rhs.name = callback, cbdata.get(rhs, rhs)
        for arg in node._kws.keys():
            node._kws[arg] = visit_vars_inner(node._kws[arg], callback, cbdata)
    return node