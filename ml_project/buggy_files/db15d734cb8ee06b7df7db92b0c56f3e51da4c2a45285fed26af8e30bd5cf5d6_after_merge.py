def _fix_ssa_vars(blocks, varname, defmap):
    """Rewrite all uses to ``varname`` given the definition map
    """
    states = _make_states(blocks)
    states['varname'] = varname
    states['defmap'] = defmap
    states['phimap'] = phimap = defaultdict(list)
    states['cfg'] = cfg = compute_cfg_from_blocks(blocks)
    states['df+'] = _iterated_domfronts(cfg)
    newblocks = _run_block_rewrite(blocks, states, _FixSSAVars())
    # check for unneeded phi nodes
    _remove_unneeded_phis(phimap)
    # insert phi nodes
    for label, philist in phimap.items():
        curblk = newblocks[label]
        # Prepend PHI nodes to the block
        curblk.body = philist + curblk.body
    return newblocks