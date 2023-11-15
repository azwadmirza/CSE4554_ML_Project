def mk_alloc(typemap, calltypes, lhs, size_var, dtype, scope, loc):
    """generate an array allocation with np.empty() and return list of nodes.
    size_var can be an int variable or tuple of int variables.
    """
    out = []
    ndims = 1
    size_typ = types.intp
    if isinstance(size_var, tuple):
        if len(size_var) == 1:
            size_var = size_var[0]
        else:
            # tuple_var = build_tuple([size_var...])
            ndims = len(size_var)
            tuple_var = ir.Var(scope, mk_unique_var("$tuple_var"), loc)
            if typemap:
                typemap[tuple_var.name] = types.containers.UniTuple(types.intp, ndims)
            # constant sizes need to be assigned to vars
            new_sizes = []
            for size in size_var:
                if isinstance(size, ir.Var):
                    new_size = size
                else:
                    assert isinstance(size, int)
                    new_size = ir.Var(scope, mk_unique_var("$alloc_size"), loc)
                    if typemap:
                        typemap[new_size.name] = types.intp
                    size_assign = ir.Assign(ir.Const(size, loc), new_size, loc)
                    out.append(size_assign)
                new_sizes.append(new_size)
            tuple_call = ir.Expr.build_tuple(new_sizes, loc)
            tuple_assign = ir.Assign(tuple_call, tuple_var, loc)
            out.append(tuple_assign)
            size_var = tuple_var
            size_typ = types.containers.UniTuple(types.intp, ndims)
    # g_np_var = Global(numpy)
    g_np_var = ir.Var(scope, mk_unique_var("$np_g_var"), loc)
    if typemap:
        typemap[g_np_var.name] = types.misc.Module(numpy)
    g_np = ir.Global('np', numpy, loc)
    g_np_assign = ir.Assign(g_np, g_np_var, loc)
    # attr call: empty_attr = getattr(g_np_var, empty)
    empty_attr_call = ir.Expr.getattr(g_np_var, "empty", loc)
    attr_var = ir.Var(scope, mk_unique_var("$empty_attr_attr"), loc)
    if typemap:
        typemap[attr_var.name] = get_np_ufunc_typ(numpy.empty)
    attr_assign = ir.Assign(empty_attr_call, attr_var, loc)
    # alloc call: lhs = empty_attr(size_var, typ_var)
    typ_var = ir.Var(scope, mk_unique_var("$np_typ_var"), loc)
    if typemap:
        typemap[typ_var.name] = types.functions.NumberClass(dtype)
    # assuming str(dtype) returns valid np dtype string
    np_typ_getattr = ir.Expr.getattr(g_np_var, str(dtype), loc)
    typ_var_assign = ir.Assign(np_typ_getattr, typ_var, loc)
    alloc_call = ir.Expr.call(attr_var, [size_var, typ_var], (), loc)
    if calltypes:
        calltypes[alloc_call] = typemap[attr_var.name].get_call_type(
            typing.Context(), [size_typ, types.functions.NumberClass(dtype)], {})
    #signature(
    #    types.npytypes.Array(dtype, ndims, 'C'), size_typ,
    #    types.functions.NumberClass(dtype))
    alloc_assign = ir.Assign(alloc_call, lhs, loc)

    out.extend([g_np_assign, attr_assign, typ_var_assign, alloc_assign])
    return out