def remove_dead(blocks, args, func_ir, typemap=None, alias_map=None, arg_aliases=None):
    """dead code elimination using liveness and CFG info.
    Returns True if something has been removed, or False if nothing is removed.
    """
    cfg = compute_cfg_from_blocks(blocks)
    usedefs = compute_use_defs(blocks)
    live_map = compute_live_map(cfg, blocks, usedefs.usemap, usedefs.defmap)
    call_table, _ = get_call_table(blocks)
    if alias_map is None or arg_aliases is None:
        alias_map, arg_aliases = find_potential_aliases(blocks, args, typemap,
                                                        func_ir)
    if config.DEBUG_ARRAY_OPT == 1:
        print("alias map:", alias_map)
    # keep set for easier search
    alias_set = set(alias_map.keys())

    removed = False
    for label, block in blocks.items():
        # find live variables at each statement to delete dead assignment
        lives = {v.name for v in block.terminator.list_vars()}
        # find live variables at the end of block
        for out_blk, _data in cfg.successors(label):
            lives |= live_map[out_blk]
        removed |= remove_dead_block(block, lives, call_table, arg_aliases,
                                     alias_map, alias_set, func_ir, typemap)
    return removed