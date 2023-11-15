def get_parfor_params(parfor):
    """find variables used in body of parfor from outside.
    computed as live variables at entry of first block.
    """
    blocks = wrap_parfor_blocks(parfor)
    cfg = compute_cfg_from_blocks(blocks)
    usedefs = compute_use_defs(blocks)
    live_map = compute_live_map(cfg, blocks, usedefs.usemap, usedefs.defmap)
    unwrap_parfor_blocks(parfor)
    keylist = sorted(live_map.keys())
    first_non_init_block = keylist[1]

    # remove parfor index variables since they are not input
    for l in parfor.loop_nests:
        live_map[first_non_init_block] -= {l.index_variable.name}

    return sorted(live_map[first_non_init_block])