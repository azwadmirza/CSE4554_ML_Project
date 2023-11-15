def simplify(func_ir, typemap, calltypes):
    remove_dels(func_ir.blocks)
    # get copies in to blocks and out from blocks
    in_cps, out_cps = copy_propagate(func_ir.blocks, typemap)
    # table mapping variable names to ir.Var objects to help replacement
    name_var_table = get_name_var_table(func_ir.blocks)
    save_copies = apply_copy_propagate(
        func_ir.blocks,
        in_cps,
        name_var_table,
        typemap,
        calltypes)
    restore_copy_var_names(func_ir.blocks, save_copies, typemap)
    # remove dead code to enable fusion
    remove_dead(func_ir.blocks, func_ir.arg_names, func_ir, typemap)
    func_ir.blocks = simplify_CFG(func_ir.blocks)
    if config.DEBUG_ARRAY_OPT == 1:
        dprint_func_ir(func_ir, "after simplify")