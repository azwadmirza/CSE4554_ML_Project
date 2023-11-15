def remove_dead(blocks, args):
    """dead code elimination using liveness and CFG info.
    Returns True if something has been removed, or False if nothing is removed."""
    cfg = compute_cfg_from_blocks(blocks)
    usedefs = compute_use_defs(blocks)
    live_map = compute_live_map(cfg, blocks, usedefs.usemap, usedefs.defmap)
    arg_aliases = find_potential_aliases(blocks, args)
    call_table,_ = get_call_table(blocks)

    removed = False
    for label, block in blocks.items():
        # find live variables at each statement to delete dead assignment
        lives = { v.name for v in block.terminator.list_vars() }
        # find live variables at the end of block
        for out_blk, _data in cfg.successors(label):
            lives |= live_map[out_blk]
        if label in cfg.exit_points():
            lives |= arg_aliases
        removed |= remove_dead_block(block, lives, call_table, arg_aliases)
    return removed