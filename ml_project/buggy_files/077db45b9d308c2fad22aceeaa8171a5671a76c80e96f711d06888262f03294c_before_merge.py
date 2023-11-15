def _create_gufunc_for_parfor_body(
        lowerer,
        parfor,
        typemap,
        typingctx,
        targetctx,
        flags,
        locals,
        has_aliases,
        index_var_typ,
        races):
    '''
    Takes a parfor and creates a gufunc function for its body.
    There are two parts to this function.
    1) Code to iterate across the iteration space as defined by the schedule.
    2) The parfor body that does the work for a single point in the iteration space.
    Part 1 is created as Python text for simplicity with a sentinel assignment to mark the point
    in the IR where the parfor body should be added.
    This Python text is 'exec'ed into existence and its IR retrieved with run_frontend.
    The IR is scanned for the sentinel assignment where that basic block is split and the IR
    for the parfor body inserted.
    '''

    loc = parfor.init_block.loc

    # The parfor body and the main function body share ir.Var nodes.
    # We have to do some replacements of Var names in the parfor body to make them
    # legal parameter names.  If we don't copy then the Vars in the main function also
    # would incorrectly change their name.
    loop_body = copy.copy(parfor.loop_body)
    remove_dels(loop_body)

    parfor_dim = len(parfor.loop_nests)
    loop_indices = [l.index_variable.name for l in parfor.loop_nests]

    # Get all the parfor params.
    parfor_params = parfor.params
    # Get just the outputs of the parfor.
    parfor_outputs = numba.parfor.get_parfor_outputs(parfor, parfor_params)
    # Get all parfor reduction vars, and operators.
    typemap = lowerer.fndesc.typemap
    parfor_redvars, parfor_reddict = numba.parfor.get_parfor_reductions(
        parfor, parfor_params, lowerer.fndesc.calltypes)
    # Compute just the parfor inputs as a set difference.
    parfor_inputs = sorted(
        list(
            set(parfor_params) -
            set(parfor_outputs) -
            set(parfor_redvars)))

    races = races.difference(set(parfor_redvars))
    for race in races:
        msg = ("Variable %s used in parallel loop may be written "
               "to simultaneously by multiple workers and may result "
               "in non-deterministic or unintended results." % race)
        warnings.warn(NumbaParallelSafetyWarning(msg, loc))
    replace_var_with_array(races, loop_body, typemap, lowerer.fndesc.calltypes)

    if config.DEBUG_ARRAY_OPT >= 1:
        print("parfor_params = ", parfor_params, " ", type(parfor_params))
        print("parfor_outputs = ", parfor_outputs, " ", type(parfor_outputs))
        print("parfor_inputs = ", parfor_inputs, " ", type(parfor_inputs))
        print("parfor_redvars = ", parfor_redvars, " ", type(parfor_redvars))

    # Reduction variables are represented as arrays, so they go under
    # different names.
    parfor_redarrs = []
    parfor_red_arg_types = []
    for var in parfor_redvars:
        arr = var + "_arr"
        parfor_redarrs.append(arr)
        redarraytype = redtyp_to_redarraytype(typemap[var])
        parfor_red_arg_types.append(redarraytype)
        redarrsig = redarraytype_to_sig(redarraytype)
        if arr in typemap:
            assert(typemap[arr] == redarrsig)
        else:
            typemap[arr] = redarrsig

    # Reorder all the params so that inputs go first then outputs.
    parfor_params = parfor_inputs + parfor_outputs + parfor_redarrs

    if config.DEBUG_ARRAY_OPT >= 1:
        print("parfor_params = ", parfor_params, " ", type(parfor_params))
        print("loop_indices = ", loop_indices, " ", type(loop_indices))
        print("loop_body = ", loop_body, " ", type(loop_body))
        _print_body(loop_body)

    # Some Var are not legal parameter names so create a dict of potentially illegal
    # param name to guaranteed legal name.
    param_dict = legalize_names_with_typemap(parfor_params + parfor_redvars, typemap)
    if config.DEBUG_ARRAY_OPT >= 1:
        print(
            "param_dict = ",
            sorted(
                param_dict.items()),
            " ",
            type(param_dict))

    # Some loop_indices are not legal parameter names so create a dict of potentially illegal
    # loop index to guaranteed legal name.
    ind_dict = legalize_names_with_typemap(loop_indices, typemap)
    # Compute a new list of legal loop index names.
    legal_loop_indices = [ind_dict[v] for v in loop_indices]
    if config.DEBUG_ARRAY_OPT >= 1:
        print("ind_dict = ", sorted(ind_dict.items()), " ", type(ind_dict))
        print(
            "legal_loop_indices = ",
            legal_loop_indices,
            " ",
            type(legal_loop_indices))
        for pd in parfor_params:
            print("pd = ", pd)
            print("pd type = ", typemap[pd], " ", type(typemap[pd]))

    # Get the types of each parameter.
    param_types = [typemap[v] for v in parfor_params]
    # Calculate types of args passed to gufunc.
    func_arg_types = [typemap[v] for v in (parfor_inputs + parfor_outputs)] + parfor_red_arg_types

    # Replace illegal parameter names in the loop body with legal ones.
    replace_var_names(loop_body, param_dict)
    # remember the name before legalizing as the actual arguments
    parfor_args = parfor_params
    # Change parfor_params to be legal names.
    parfor_params = [param_dict[v] for v in parfor_params]
    parfor_params_orig = parfor_params

    parfor_params = []
    ascontig = False
    for pindex in range(len(parfor_params_orig)):
        if (ascontig and
            pindex < len(parfor_inputs) and
            isinstance(param_types[pindex], types.npytypes.Array)):
            parfor_params.append(parfor_params_orig[pindex]+"param")
        else:
            parfor_params.append(parfor_params_orig[pindex])

    # Change parfor body to replace illegal loop index vars with legal ones.
    replace_var_names(loop_body, ind_dict)
    loop_body_var_table = get_name_var_table(loop_body)
    sentinel_name = get_unused_var_name("__sentinel__", loop_body_var_table)

    if config.DEBUG_ARRAY_OPT >= 1:
        print(
            "legal parfor_params = ",
            parfor_params,
            " ",
            type(parfor_params))

    # Determine the unique names of the scheduling and gufunc functions.
    # sched_func_name = "__numba_parfor_sched_%s" % (hex(hash(parfor)).replace("-", "_"))
    gufunc_name = "__numba_parfor_gufunc_%s" % (
        hex(hash(parfor)).replace("-", "_"))
    if config.DEBUG_ARRAY_OPT:
        # print("sched_func_name ", type(sched_func_name), " ", sched_func_name)
        print("gufunc_name ", type(gufunc_name), " ", gufunc_name)

    gufunc_txt = ""

    # Create the gufunc function.
    gufunc_txt += "def " + gufunc_name + \
        "(sched, " + (", ".join(parfor_params)) + "):\n"

    for pindex in range(len(parfor_inputs)):
        if ascontig and isinstance(param_types[pindex], types.npytypes.Array):
            gufunc_txt += ("    " + parfor_params_orig[pindex]
                + " = np.ascontiguousarray(" + parfor_params[pindex] + ")\n")

    # Add initialization of reduction variables
    for arr, var in zip(parfor_redarrs, parfor_redvars):
        # If reduction variable is a scalar then save current value to
        # temp and accumulate on that temp to prevent false sharing.
        if redtyp_is_scalar(typemap[var]):
            gufunc_txt += "    " + param_dict[var] + \
                 "=" + param_dict[arr] + "[0]\n"
        else:
            # The reduction variable is an array so np.copy it to a temp.
            gufunc_txt += "    " + param_dict[var] + \
                 "=np.copy(" + param_dict[arr] + ")\n"

    # For each dimension of the parfor, create a for loop in the generated gufunc function.
    # Iterate across the proper values extracted from the schedule.
    # The form of the schedule is start_dim0, start_dim1, ..., start_dimN, end_dim0,
    # end_dim1, ..., end_dimN
    for eachdim in range(parfor_dim):
        for indent in range(eachdim + 1):
            gufunc_txt += "    "
        sched_dim = eachdim
        gufunc_txt += ("for " +
                       legal_loop_indices[eachdim] +
                       " in range(sched[" +
                       str(sched_dim) +
                       "], sched[" +
                       str(sched_dim +
                           parfor_dim) +
                       "] + np.uint8(1)):\n")

    if config.DEBUG_ARRAY_OPT_RUNTIME:
        for indent in range(parfor_dim + 1):
            gufunc_txt += "    "
        gufunc_txt += "print("
        for eachdim in range(parfor_dim):
            gufunc_txt += "\"" + legal_loop_indices[eachdim] + "\"," + legal_loop_indices[eachdim] + ","
        gufunc_txt += ")\n"

    # Add the sentinel assignment so that we can find the loop body position
    # in the IR.
    for indent in range(parfor_dim + 1):
        gufunc_txt += "    "
    gufunc_txt += sentinel_name + " = 0\n"
    # Add assignments of reduction variables (for returning the value)
    redargstartdim = {}
    for arr, var in zip(parfor_redarrs, parfor_redvars):
        # After the gufunc loops, copy the accumulated temp value back to reduction array.
        if redtyp_is_scalar(typemap[var]):
            gufunc_txt += "    " + param_dict[arr] + \
                "[0] = " + param_dict[var] + "\n"
            redargstartdim[arr] = 1
        else:
            # After the gufunc loops, copy the accumulated temp array back to reduction array with ":"
            gufunc_txt += "    " + param_dict[arr] + \
                "[:] = " + param_dict[var] + "[:]\n"
            redargstartdim[arr] = 0
    gufunc_txt += "    return None\n"

    if config.DEBUG_ARRAY_OPT:
        print("gufunc_txt = ", type(gufunc_txt), "\n", gufunc_txt)
    # Force gufunc outline into existence.
    globls = {"np": np}
    locls = {}
    exec_(gufunc_txt, globls, locls)
    gufunc_func = locls[gufunc_name]

    if config.DEBUG_ARRAY_OPT:
        print("gufunc_func = ", type(gufunc_func), "\n", gufunc_func)
    # Get the IR for the gufunc outline.
    gufunc_ir = compiler.run_frontend(gufunc_func)

    if config.DEBUG_ARRAY_OPT:
        print("gufunc_ir dump ", type(gufunc_ir))
        gufunc_ir.dump()
        print("loop_body dump ", type(loop_body))
        _print_body(loop_body)

    # rename all variables in gufunc_ir afresh
    var_table = get_name_var_table(gufunc_ir.blocks)
    new_var_dict = {}
    reserved_names = [sentinel_name] + \
        list(param_dict.values()) + legal_loop_indices
    for name, var in var_table.items():
        if not (name in reserved_names):
            new_var_dict[name] = mk_unique_var(name)
    replace_var_names(gufunc_ir.blocks, new_var_dict)
    if config.DEBUG_ARRAY_OPT:
        print("gufunc_ir dump after renaming ")
        gufunc_ir.dump()

    gufunc_param_types = [
        numba.types.npytypes.Array(
            index_var_typ, 1, "C")] + param_types
    if config.DEBUG_ARRAY_OPT:
        print(
            "gufunc_param_types = ",
            type(gufunc_param_types),
            "\n",
            gufunc_param_types)

    gufunc_stub_last_label = max(gufunc_ir.blocks.keys()) + 1

    # Add gufunc stub last label to each parfor.loop_body label to prevent
    # label conflicts.
    loop_body = add_offset_to_labels(loop_body, gufunc_stub_last_label)
    # new label for splitting sentinel block
    new_label = max(loop_body.keys()) + 1

    # If enabled, add a print statement after every assignment.
    if config.DEBUG_ARRAY_OPT_RUNTIME:
        for label, block in loop_body.items():
            new_block = block.copy()
            new_block.clear()
            loc = block.loc
            scope = block.scope
            for inst in block.body:
                new_block.append(inst)
                # Append print after assignment
                if isinstance(inst, ir.Assign):
                    # Only apply to numbers
                    if typemap[inst.target.name] not in types.number_domain:
                        continue

                    # Make constant string
                    strval = "{} =".format(inst.target.name)
                    strconsttyp = types.StringLiteral(strval)

                    lhs = ir.Var(scope, mk_unique_var("str_const"), loc)
                    assign_lhs = ir.Assign(value=ir.Const(value=strval, loc=loc),
                                           target=lhs, loc=loc)
                    typemap[lhs.name] = strconsttyp
                    new_block.append(assign_lhs)

                    # Make print node
                    print_node = ir.Print(args=[lhs, inst.target], vararg=None, loc=loc)
                    new_block.append(print_node)
                    sig = numba.typing.signature(types.none,
                                           typemap[lhs.name],
                                           typemap[inst.target.name])
                    lowerer.fndesc.calltypes[print_node] = sig
            loop_body[label] = new_block

    if config.DEBUG_ARRAY_OPT:
        print("parfor loop body")
        _print_body(loop_body)

    wrapped_blocks = wrap_loop_body(loop_body)
    hoisted, not_hoisted = hoist(parfor_params, loop_body, typemap, wrapped_blocks)
    start_block = gufunc_ir.blocks[min(gufunc_ir.blocks.keys())]
    start_block.body = start_block.body[:-1] + hoisted + [start_block.body[-1]]
    unwrap_loop_body(loop_body)

    # store hoisted into diagnostics
    diagnostics = lowerer.metadata['parfor_diagnostics']
    diagnostics.hoist_info[parfor.id] = {'hoisted': hoisted,
                                         'not_hoisted': not_hoisted}

    if config.DEBUG_ARRAY_OPT:
        print("After hoisting")
        _print_body(loop_body)

    # Search all the block in the gufunc outline for the sentinel assignment.
    for label, block in gufunc_ir.blocks.items():
        for i, inst in enumerate(block.body):
            if isinstance(
                    inst,
                    ir.Assign) and inst.target.name == sentinel_name:
                # We found the sentinel assignment.
                loc = inst.loc
                scope = block.scope
                # split block across __sentinel__
                # A new block is allocated for the statements prior to the sentinel
                # but the new block maintains the current block label.
                prev_block = ir.Block(scope, loc)
                prev_block.body = block.body[:i]
                # The current block is used for statements after the sentinel.
                block.body = block.body[i + 1:]
                # But the current block gets a new label.
                body_first_label = min(loop_body.keys())

                # The previous block jumps to the minimum labelled block of the
                # parfor body.
                prev_block.append(ir.Jump(body_first_label, loc))
                # Add all the parfor loop body blocks to the gufunc function's
                # IR.
                for (l, b) in loop_body.items():
                    gufunc_ir.blocks[l] = b
                body_last_label = max(loop_body.keys())
                gufunc_ir.blocks[new_label] = block
                gufunc_ir.blocks[label] = prev_block
                # Add a jump from the last parfor body block to the block containing
                # statements after the sentinel.
                gufunc_ir.blocks[body_last_label].append(
                    ir.Jump(new_label, loc))
                break
        else:
            continue
        break

    if config.DEBUG_ARRAY_OPT:
        print("gufunc_ir last dump before renaming")
        gufunc_ir.dump()

    gufunc_ir.blocks = rename_labels(gufunc_ir.blocks)
    remove_dels(gufunc_ir.blocks)

    if config.DEBUG_ARRAY_OPT:
        print("gufunc_ir last dump")
        gufunc_ir.dump()
        print("flags", flags)
        print("typemap", typemap)

    old_alias = flags.noalias
    if not has_aliases:
        if config.DEBUG_ARRAY_OPT:
            print("No aliases found so adding noalias flag.")
        flags.noalias = True
    kernel_func = compiler.compile_ir(
        typingctx,
        targetctx,
        gufunc_ir,
        gufunc_param_types,
        types.none,
        flags,
        locals)

    flags.noalias = old_alias

    kernel_sig = signature(types.none, *gufunc_param_types)
    if config.DEBUG_ARRAY_OPT:
        print("kernel_sig = ", kernel_sig)

    return kernel_func, parfor_args, kernel_sig, redargstartdim, func_arg_types