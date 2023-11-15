def lower_parfor_sequential(func_ir, typemap, calltypes):
    ir_utils._max_label = ir_utils.find_max_label(func_ir.blocks) + 1

    parfor_found = False
    new_blocks = {}
    for (block_label, block) in func_ir.blocks.items():
        block_label, parfor_found = _lower_parfor_sequential_block(
            block_label, block, new_blocks, typemap, calltypes, parfor_found)
        # old block stays either way
        new_blocks[block_label] = block
    func_ir.blocks = new_blocks
    dprint_func_ir(func_ir, "before rename")
    # rename only if parfor found and replaced (avoid test_flow_control error)
    if parfor_found:
        func_ir.blocks = rename_labels(func_ir.blocks)
    dprint_func_ir(func_ir, "after parfor sequential lowering")
    local_array_analysis = array_analysis.ArrayAnalysis(func_ir, typemap, calltypes)
    simplify(func_ir, typemap, local_array_analysis,
             calltypes, array_analysis.copy_propagate_update_analysis)
    dprint_func_ir(func_ir, "after parfor sequential simplify")

    return