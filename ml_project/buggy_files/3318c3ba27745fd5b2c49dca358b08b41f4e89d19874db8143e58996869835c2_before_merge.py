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