def _inline_const_arraycall(block, func_ir, context, typemap, calltypes):
    """Look for array(list) call where list is a constant list created by build_list,
    and turn them into direct array creation and initialization, if the following
    conditions are met:
      1. The build_list call immediate preceeds the array call;
      2. The list variable is no longer live after array call;
    If any condition check fails, no modification will be made.
    """
    debug_print = _make_debug_print("inline_const_arraycall")
    scope = block.scope

    def inline_array(array_var, expr, stmts, list_vars, dels):
        """Check to see if the given "array_var" is created from a list
        of constants, and try to inline the list definition as array
        initialization.

        Extra statements produced with be appended to "stmts".
        """
        callname = guard(find_callname, func_ir, expr)
        require(callname and callname[1] == 'numpy' and callname[0] == 'array')
        require(expr.args[0].name in list_vars)
        ret_type = calltypes[expr].return_type
        require(isinstance(ret_type, types.ArrayCompatible) and
                           ret_type.ndim == 1)
        loc = expr.loc
        list_var = expr.args[0]
        array_typ = typemap[array_var.name]
        debug_print("inline array_var = ", array_var, " list_var = ", list_var)
        dtype = array_typ.dtype
        seq, op = find_build_sequence(func_ir, list_var)
        size = len(seq)
        size_var = ir.Var(scope, mk_unique_var("size"), loc)
        size_tuple_var = ir.Var(scope, mk_unique_var("size_tuple"), loc)
        size_typ = types.intp
        size_tuple_typ = types.UniTuple(size_typ, 1)

        typemap[size_var.name] = size_typ
        typemap[size_tuple_var.name] = size_tuple_typ

        stmts.append(_new_definition(func_ir, size_var,
                 ir.Const(size, loc=loc), loc))

        stmts.append(_new_definition(func_ir, size_tuple_var,
                 ir.Expr.build_tuple(items=[size_var], loc=loc), loc))

        empty_func = ir.Var(scope, mk_unique_var("empty_func"), loc)
        fnty = get_np_ufunc_typ(np.empty)
        sig = context.resolve_function_type(fnty, (size_typ,), {})
        typemap[empty_func.name] = fnty #

        stmts.append(_new_definition(func_ir, empty_func,
                         ir.Global('empty', np.empty, loc=loc), loc))

        empty_call = ir.Expr.call(empty_func, [size_var], {}, loc=loc)
        calltypes[empty_call] = typing.signature(array_typ, size_typ)
        stmts.append(_new_definition(func_ir, array_var, empty_call, loc))

        for i in range(size):
            index_var = ir.Var(scope, mk_unique_var("index"), loc)
            index_typ = types.intp
            typemap[index_var.name] = index_typ
            stmts.append(_new_definition(func_ir, index_var,
                    ir.Const(i, loc), loc))
            setitem = ir.SetItem(array_var, index_var, seq[i], loc)
            calltypes[setitem] = typing.signature(types.none, array_typ,
                                                  index_typ, dtype)
            stmts.append(setitem)

        stmts.extend(dels)
        return True

    # list_vars keep track of the variable created from the latest
    # build_list instruction, as well as its synonyms.
    list_vars = []
    # dead_vars keep track of those in list_vars that are considered dead.
    dead_vars = []
    # list_items keep track of the elements used in build_list.
    list_items = []
    stmts = []
    # dels keep track of the deletion of list_items, which will need to be
    # moved after array initialization.
    dels = []
    modified = False
    for inst in block.body:
        if isinstance(inst, ir.Assign):
            if isinstance(inst.value, ir.Var):
                if inst.value.name in list_vars:
                    list_vars.append(inst.target.name)
                    stmts.append(inst)
                    continue
            elif isinstance(inst.value, ir.Expr):
                expr = inst.value
                if expr.op == 'build_list':
                    list_vars = [inst.target.name]
                    list_items = [x.name for x in expr.items]
                    stmts.append(inst)
                    continue
                elif expr.op == 'call' and expr in calltypes:
                    arr_var = inst.target
                    if guard(inline_array, inst.target, expr,
                                           stmts, list_vars, dels):
                        modified = True
                        continue
        elif isinstance(inst, ir.Del):
            removed_var = inst.value
            if removed_var in list_items:
                dels.append(inst)
                continue
            elif removed_var in list_vars:
                # one of the list_vars is considered dead.
                dead_vars.append(removed_var)
                list_vars.remove(removed_var)
                stmts.append(inst)
                if list_vars == []:
                    # if all list_vars are considered dead, we need to filter
                    # them out from existing stmts to completely remove
                    # build_list.
                    # Note that if a translation didn't take place, dead_vars
                    # will also be empty when we reach this point.
                    body = []
                    for inst in stmts:
                        if ((isinstance(inst, ir.Assign) and
                             inst.target.name in dead_vars) or
                             (isinstance(inst, ir.Del) and
                             inst.value in dead_vars)):
                            continue
                        body.append(inst)
                    stmts = body
                    dead_vars = []
                    modified = True
                    continue
        stmts.append(inst)

        # If the list is used in any capacity between build_list and array
        # call, then we must call off the translation for this list because
        # it could be mutated and list_items would no longer be applicable.
        list_var_used = any([ x.name in list_vars for x in inst.list_vars() ])
        if list_var_used:
            list_vars = []
            dead_vars = []
            list_items = []
            dels = []

    return stmts if modified else None