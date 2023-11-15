def get_parfor_params(blocks, options_fusion, fusion_info):
    """find variables used in body of parfors from outside and save them.
    computed as live variables at entry of first block.
    """

    # since parfor wrap creates a back-edge to first non-init basic block,
    # live_map[first_non_init_block] contains variables defined in parfor body
    # that could be undefined before. So we only consider variables that are
    # actually defined before the parfor body in the program.
    parfor_ids = set()
    pre_defs = set()
    _, all_defs = compute_use_defs(blocks)
    topo_order = find_topo_order(blocks)
    for label in topo_order:
        block = blocks[label]
        for i, parfor in _find_parfors(block.body):
            # find variable defs before the parfor in the same block
            dummy_block = ir.Block(block.scope, block.loc)
            dummy_block.body = block.body[:i]
            before_defs = compute_use_defs({0: dummy_block}).defmap[0]
            pre_defs |= before_defs
            parfor.params = get_parfor_params_inner(parfor, pre_defs, options_fusion, fusion_info) | parfor.races
            parfor_ids.add(parfor.id)

        pre_defs |= all_defs[label]
    return parfor_ids