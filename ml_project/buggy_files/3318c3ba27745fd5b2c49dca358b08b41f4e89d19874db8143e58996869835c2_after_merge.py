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
        # Get the type of the array to be created.
        array_typ = typemap[array_var.name]
        debug_print("inline array_var = ", array_var, " list_var = ", list_var)
        # Get the element type of the array to be created.
        dtype = array_typ.dtype
        # Get the sequence of operations to provide values to the new array.
        seq, _ = find_build_sequence(func_ir, list_var)
        size = len(seq)
        # Create a tuple to pass to empty below to specify the new array size.
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

        # The general approach is to create an empty array and then fill
        # the elements in one-by-one from their specificiation.

        # Get the numpy type to pass to empty.
        nptype = types.DType(dtype)

        # Create a variable to hold the numpy empty function.
        empty_func = ir.Var(scope, mk_unique_var("empty_func"), loc)
        fnty = get_np_ufunc_typ(np.empty)
        sig = context.resolve_function_type(fnty, (size_typ,), {'dtype':nptype})

        typemap[empty_func.name] = fnty

        stmts.append(_new_definition(func_ir, empty_func,
                         ir.Global('empty', np.empty, loc=loc), loc))

        # We pass two arguments to empty, first the size tuple and second
        # the dtype of the new array.  Here, we created typ_var which is
        # the dtype argument of the new array.  typ_var in turn is created
        # by getattr of the dtype string on the numpy module.

        # Create var for numpy module.
        g_np_var = ir.Var(scope, mk_unique_var("$np_g_var"), loc)
        typemap[g_np_var.name] = types.misc.Module(np)
        g_np = ir.Global('np', np, loc)
        stmts.append(_new_definition(func_ir, g_np_var, g_np, loc))

        # Create var for result of numpy.<dtype>.
        typ_var = ir.Var(scope, mk_unique_var("$np_typ_var"), loc)
        typemap[typ_var.name] = nptype
        dtype_str = str(dtype)
        if dtype_str == 'bool':
            dtype_str = 'bool_'
        # Get dtype attribute of numpy module.
        np_typ_getattr = ir.Expr.getattr(g_np_var, dtype_str, loc)
        stmts.append(_new_definition(func_ir, typ_var, np_typ_getattr, loc))

        # Create the call to numpy.empty passing the size tuple and dtype var.
        empty_call = ir.Expr.call(empty_func, [size_var, typ_var], {}, loc=loc)
        calltypes[empty_call] = typing.signature(array_typ, size_typ, nptype)
        stmts.append(_new_definition(func_ir, array_var, empty_call, loc))

        # Fill in the new empty array one-by-one.
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