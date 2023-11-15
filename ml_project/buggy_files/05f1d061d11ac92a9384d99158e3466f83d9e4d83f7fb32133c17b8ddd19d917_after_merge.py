def _lower_parfor_parallel(lowerer, parfor):
    from .parallel import get_thread_count

    """Lowerer that handles LLVM code generation for parfor.
    This function lowers a parfor IR node to LLVM.
    The general approach is as follows:
    1) The code from the parfor's init block is lowered normally
       in the context of the current function.
    2) The body of the parfor is transformed into a gufunc function.
    3) Code is inserted into the main function that calls do_scheduling
       to divide the iteration space for each thread, allocates
       reduction arrays, calls the gufunc function, and then invokes
       the reduction function across the reduction arrays to produce
       the final reduction values.
    """
    typingctx = lowerer.context.typing_context
    targetctx = lowerer.context
    # We copy the typemap here because for race condition variable we'll
    # update their type to array so they can be updated by the gufunc.
    orig_typemap = lowerer.fndesc.typemap
    # replace original typemap with copy and restore the original at the end.
    lowerer.fndesc.typemap = copy.copy(orig_typemap)
    typemap = lowerer.fndesc.typemap
    varmap = lowerer.varmap

    if config.DEBUG_ARRAY_OPT:
        print("_lower_parfor_parallel")
        parfor.dump()

    loc = parfor.init_block.loc
    scope = parfor.init_block.scope

    # produce instructions for init_block
    if config.DEBUG_ARRAY_OPT:
        print("init_block = ", parfor.init_block, " ", type(parfor.init_block))
    for instr in parfor.init_block.body:
        if config.DEBUG_ARRAY_OPT:
            print("lower init_block instr = ", instr)
        lowerer.lower_inst(instr)

    for racevar in parfor.races:
        if racevar not in varmap:
            rvtyp = typemap[racevar]
            rv = ir.Var(scope, racevar, loc)
            lowerer._alloca_var(rv.name, rvtyp)

    alias_map = {}
    arg_aliases = {}
    numba.parfor.find_potential_aliases_parfor(parfor, parfor.params, typemap,
                                        lowerer.func_ir, alias_map, arg_aliases)
    if config.DEBUG_ARRAY_OPT:
        print("alias_map", alias_map)
        print("arg_aliases", arg_aliases)

    # run get_parfor_outputs() and get_parfor_reductions() before gufunc creation
    # since Jumps are modified so CFG of loop_body dict will become invalid
    assert parfor.params != None

    parfor_output_arrays = numba.parfor.get_parfor_outputs(
        parfor, parfor.params)
    parfor_redvars, parfor_reddict = numba.parfor.get_parfor_reductions(
        parfor, parfor.params, lowerer.fndesc.calltypes)

    # init reduction array allocation here.
    nredvars = len(parfor_redvars)
    redarrs = {}
    if nredvars > 0:
        # reduction arrays outer dimension equal to thread count
        thread_count = get_thread_count()
        scope = parfor.init_block.scope
        loc = parfor.init_block.loc

        # For each reduction variable...
        for i in range(nredvars):
            redvar_typ = lowerer.fndesc.typemap[parfor_redvars[i]]
            redvar = ir.Var(scope, parfor_redvars[i], loc)
            redarrvar_typ = redtyp_to_redarraytype(redvar_typ)
            reddtype = redarrvar_typ.dtype
            if config.DEBUG_ARRAY_OPT:
                print("redvar_typ", redvar_typ, redarrvar_typ, reddtype, types.DType(reddtype))

            # If this is reduction over an array,
            # the reduction array has just one added per-worker dimension.
            if isinstance(redvar_typ, types.npytypes.Array):
                redarrdim = redvar_typ.ndim + 1
            else:
                redarrdim = 1

            # Reduction array is created and initialized to the initial reduction value.

            # First create a var for the numpy empty ufunc.
            empty_func = ir.Var(scope, mk_unique_var("empty_func"), loc)
            ff_fnty = get_np_ufunc_typ(np.empty)
            ff_sig = typingctx.resolve_function_type(ff_fnty,
                                            (types.UniTuple(types.intp, redarrdim),
                                             types.DType(reddtype)), {})
            typemap[empty_func.name] = ff_fnty
            empty_assign = ir.Assign(ir.Global("empty", np.empty, loc=loc), empty_func, loc)
            lowerer.lower_inst(empty_assign)

            # Create var for outer dimension size of reduction array equal to number of threads.
            num_threads_var = ir.Var(scope, mk_unique_var("num_threads"), loc)
            num_threads_assign = ir.Assign(ir.Const(thread_count, loc), num_threads_var, loc)
            typemap[num_threads_var.name] = types.intp
            lowerer.lower_inst(num_threads_assign)

            # Empty call takes tuple of sizes.  Create here and fill in outer dimension (num threads).
            size_var = ir.Var(scope, mk_unique_var("tuple_size_var"), loc)
            typemap[size_var.name] = types.UniTuple(types.intp, redarrdim)
            size_var_list = [num_threads_var]

            # If this is a reduction over an array...
            if isinstance(redvar_typ, types.npytypes.Array):
                # Add code to get the shape of the array being reduced over.
                redshape_var = ir.Var(scope, mk_unique_var("redarr_shape"), loc)
                typemap[redshape_var.name] = types.UniTuple(types.intp, redvar_typ.ndim)
                redshape_getattr = ir.Expr.getattr(redvar, "shape", loc)
                redshape_assign = ir.Assign(redshape_getattr, redshape_var, loc)
                lowerer.lower_inst(redshape_assign)

                # Add the dimension sizes of the array being reduced over to the tuple of sizes pass to empty.
                for j in range(redvar_typ.ndim):
                    onedimvar = ir.Var(scope, mk_unique_var("redshapeonedim"), loc)
                    onedimgetitem = ir.Expr.static_getitem(redshape_var, j, None, loc)
                    typemap[onedimvar.name] = types.intp
                    onedimassign = ir.Assign(onedimgetitem, onedimvar, loc)
                    lowerer.lower_inst(onedimassign)
                    size_var_list += [onedimvar]

            size_call = ir.Expr.build_tuple(size_var_list, loc)
            size_assign = ir.Assign(size_call, size_var, loc)
            lowerer.lower_inst(size_assign)

            # Add call to empty passing the size var tuple.
            empty_call = ir.Expr.call(empty_func, [size_var], {}, loc=loc)
            redarr_var = ir.Var(scope, mk_unique_var("redarr"), loc)
            typemap[redarr_var.name] = redarrvar_typ
            empty_call_assign = ir.Assign(empty_call, redarr_var, loc)
            lowerer.fndesc.calltypes[empty_call] = ff_sig
            lowerer.lower_inst(empty_call_assign)

            # Remember mapping of original reduction array to the newly created per-worker reduction array.
            redarrs[redvar.name] = redarr_var

            init_val = parfor_reddict[parfor_redvars[i]][0]
            if init_val != None:
                if isinstance(redvar_typ, types.npytypes.Array):
                    # Create an array of identity values for the reduction.
                    # First, create a variable for np.full.
                    full_func = ir.Var(scope, mk_unique_var("full_func"), loc)
                    full_fnty = get_np_ufunc_typ(np.full)
                    full_sig = typingctx.resolve_function_type(full_fnty,
                               (types.UniTuple(types.intp, redvar_typ.ndim),
                                reddtype,
                                types.DType(reddtype)), {})
                    typemap[full_func.name] = full_fnty
                    full_assign = ir.Assign(ir.Global("full", np.full, loc=loc), full_func, loc)
                    lowerer.lower_inst(full_assign)

                    # Then create a var with the identify value.
                    init_val_var = ir.Var(scope, mk_unique_var("init_val"), loc)
                    init_val_assign = ir.Assign(ir.Const(init_val, loc), init_val_var, loc)
                    typemap[init_val_var.name] = reddtype
                    lowerer.lower_inst(init_val_assign)

                    # Then, call np.full with the shape of the reduction array and the identity value.
                    full_call = ir.Expr.call(full_func, [redshape_var, init_val_var], {}, loc=loc)
                    lowerer.fndesc.calltypes[full_call] = full_sig
                    redtoset = ir.Var(scope, mk_unique_var("redtoset"), loc)
                    redtoset_assign = ir.Assign(full_call, redtoset, loc)
                    typemap[redtoset.name] = redvar_typ
                    lowerer.lower_inst(redtoset_assign)
                else:
                    redtoset = ir.Var(scope, mk_unique_var("redtoset"), loc)
                    redtoset_assign = ir.Assign(ir.Const(init_val, loc), redtoset, loc)
                    typemap[redtoset.name] = reddtype
                    lowerer.lower_inst(redtoset_assign)
            else:
                redtoset = redvar

            # For each thread, initialize the per-worker reduction array to the current reduction array value.
            for j in range(get_thread_count()):
                index_var = ir.Var(scope, mk_unique_var("index_var"), loc)
                index_var_assign = ir.Assign(ir.Const(j, loc), index_var, loc)
                typemap[index_var.name] = types.uintp
                lowerer.lower_inst(index_var_assign)

                redsetitem = ir.SetItem(redarr_var, index_var, redtoset, loc)
                lowerer.fndesc.calltypes[redsetitem] = signature(types.none,
                        typemap[redarr_var.name], typemap[index_var.name], redvar_typ)
                lowerer.lower_inst(redsetitem)

    # compile parfor body as a separate function to be used with GUFuncWrapper
    flags = copy.copy(parfor.flags)
    flags.set('error_model', 'numpy')
    # Can't get here unless  flags.set('auto_parallel', ParallelOptions(True))
    index_var_typ = typemap[parfor.loop_nests[0].index_variable.name]
    # index variables should have the same type, check rest of indices
    for l in parfor.loop_nests[1:]:
        assert typemap[l.index_variable.name] == index_var_typ
    numba.parfor.sequential_parfor_lowering = True
    func, func_args, func_sig, redargstartdim, func_arg_types = _create_gufunc_for_parfor_body(
        lowerer, parfor, typemap, typingctx, targetctx, flags, {},
        bool(alias_map), index_var_typ, parfor.races)
    numba.parfor.sequential_parfor_lowering = False

    # get the shape signature
    func_args = ['sched'] + func_args
    num_reductions = len(parfor_redvars)
    num_inputs = len(func_args) - len(parfor_output_arrays) - num_reductions
    if config.DEBUG_ARRAY_OPT:
        print("func_args = ", func_args)
        print("num_inputs = ", num_inputs)
        print("parfor_outputs = ", parfor_output_arrays)
        print("parfor_redvars = ", parfor_redvars)
        print("num_reductions = ", num_reductions)
    gu_signature = _create_shape_signature(
        parfor.get_shape_classes,
        num_inputs,
        num_reductions,
        func_args,
        redargstartdim,
        func_sig,
        parfor.races,
        typemap)
    if config.DEBUG_ARRAY_OPT:
        print("gu_signature = ", gu_signature)

    # call the func in parallel by wrapping it with ParallelGUFuncBuilder
    loop_ranges = [(l.start, l.stop, l.step) for l in parfor.loop_nests]
    if config.DEBUG_ARRAY_OPT:
        print("loop_nests = ", parfor.loop_nests)
        print("loop_ranges = ", loop_ranges)
    call_parallel_gufunc(
        lowerer,
        func,
        gu_signature,
        func_sig,
        func_args,
        func_arg_types,
        loop_ranges,
        parfor_redvars,
        parfor_reddict,
        redarrs,
        parfor.init_block,
        index_var_typ,
        parfor.races)
    if config.DEBUG_ARRAY_OPT:
        sys.stdout.flush()

    if nredvars > 0:
        # Perform the final reduction across the reduction array created above.
        thread_count = get_thread_count()
        scope = parfor.init_block.scope
        loc = parfor.init_block.loc

        # For each reduction variable...
        for i in range(nredvars):
            name = parfor_redvars[i]
            redarr = redarrs[name]
            redvar_typ = lowerer.fndesc.typemap[name]

            if config.DEBUG_ARRAY_OPT_RUNTIME:
                res_print_str = "res_print"
                strconsttyp = types.Const(res_print_str)
                lhs = ir.Var(scope, mk_unique_var("str_const"), loc)
                assign_lhs = ir.Assign(value=ir.Const(value=res_print_str, loc=loc),
                                               target=lhs, loc=loc)
                typemap[lhs.name] = strconsttyp
                lowerer.lower_inst(assign_lhs)

                res_print = ir.Print(args=[lhs, redarr], vararg=None, loc=loc)
                lowerer.fndesc.calltypes[res_print] = signature(types.none,
                                                         typemap[lhs.name],
                                                         typemap[redarr.name])
                print("res_print", res_print)
                lowerer.lower_inst(res_print)

            # For each element in the reduction array created above.
            for j in range(get_thread_count()):
                # Create index var to access that element.
                index_var = ir.Var(scope, mk_unique_var("index_var"), loc)
                index_var_assign = ir.Assign(ir.Const(j, loc), index_var, loc)
                typemap[index_var.name] = types.uintp
                lowerer.lower_inst(index_var_assign)

                # Read that element from the array into oneelem.
                oneelem = ir.Var(scope, mk_unique_var("redelem"), loc)
                oneelemgetitem = ir.Expr.getitem(redarr, index_var, loc)
                typemap[oneelem.name] = redvar_typ
                lowerer.fndesc.calltypes[oneelemgetitem] = signature(redvar_typ,
                        typemap[redarr.name], typemap[index_var.name])
                oneelemassign = ir.Assign(oneelemgetitem, oneelem, loc)
                lowerer.lower_inst(oneelemassign)

                init_var = ir.Var(scope, name+"#init", loc)
                init_assign = ir.Assign(oneelem, init_var, loc)
                if name+"#init" not in typemap:
                    typemap[init_var.name] = redvar_typ
                lowerer.lower_inst(init_assign)

                if config.DEBUG_ARRAY_OPT_RUNTIME:
                    res_print_str = "one_res_print"
                    strconsttyp = types.Const(res_print_str)
                    lhs = ir.Var(scope, mk_unique_var("str_const"), loc)
                    assign_lhs = ir.Assign(value=ir.Const(value=res_print_str, loc=loc),
                                               target=lhs, loc=loc)
                    typemap[lhs.name] = strconsttyp
                    lowerer.lower_inst(assign_lhs)

                    res_print = ir.Print(args=[lhs, index_var, oneelem, init_var],
                                         vararg=None, loc=loc)
                    lowerer.fndesc.calltypes[res_print] = signature(types.none,
                                                             typemap[lhs.name],
                                                             typemap[index_var.name],
                                                             typemap[oneelem.name],
                                                             typemap[init_var.name])
                    print("res_print", res_print)
                    lowerer.lower_inst(res_print)

                # generate code for combining reduction variable with thread output
                for inst in parfor_reddict[name][1]:
                    # If we have a case where a parfor body has an array reduction like A += B
                    # and A and B have different data types then the reduction in the parallel
                    # region will operate on those differeing types.  However, here, after the
                    # parallel region, we are summing across the reduction array and that is
                    # guaranteed to have the same data type so we need to change the reduction
                    # nodes so that the right-hand sides have a type equal to the reduction-type
                    # and therefore the left-hand side.
                    if isinstance(inst, ir.Assign):
                        rhs = inst.value
                        # We probably need to generalize this since it only does substitutions in
                        # inplace_ginops.
                        if isinstance(rhs, ir.Expr) and rhs.op == 'inplace_binop' and rhs.rhs.name == init_var.name:
                            # Get calltype of rhs.
                            ct = lowerer.fndesc.calltypes[rhs]
                            assert(len(ct.args) == 2)
                            # Create new arg types replace the second arg type with the reduction var type.
                            ctargs = (ct.args[0], redvar_typ)
                            # Update the signature of the call.
                            ct = ct.replace(args=ctargs)
                            # Remove so we can re-insrt since calltypes is unique dict.
                            lowerer.fndesc.calltypes.pop(rhs)
                            # Add calltype back in for the expr with updated signature.
                            lowerer.fndesc.calltypes[rhs] = ct
                    lowerer.lower_inst(inst)

    # Restore the original typemap of the function that was replaced temporarily at the
    # Beginning of this function.
    lowerer.fndesc.typemap = orig_typemap