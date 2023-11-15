def parfor_defs(parfor, use_set=None, def_set=None):
    """list variables written in this parfor by recursively
    calling compute_use_defs() on body and combining block defs.
    """
    if use_set is None:
        use_set = set()
    if def_set is None:
        def_set = set()
    blocks = wrap_parfor_blocks(parfor)
    uses, defs = compute_use_defs(blocks)
    cfg = compute_cfg_from_blocks(blocks)
    last_label = max(blocks.keys())
    unwrap_parfor_blocks(parfor)

    # Conservatively, only add defs for blocks that are definitely executed
    # Go through blocks in order, as if they are statements of the block that
    # includes the parfor, and update uses/defs.

    # no need for topo order of ir_utils
    topo_order = cfg.topo_order()
    # blocks that dominate last block are definitely executed
    definitely_executed = cfg.dominators()[last_label]
    # except loop bodies that might not execute
    for loop in cfg.loops().values():
        definitely_executed -= loop.body
    for label in topo_order:
        if label in definitely_executed:
            # see compute_use_defs() in analysis.py
            # variables defined in the block that includes the parfor are not
            # uses of that block (are not potentially live in the beginning of
            # the block)
            use_set.update(uses[label] - def_set)
            def_set.update(defs[label])
        else:
            use_set.update(uses[label] - def_set)

    # treat loop variables and size variables as use
    loop_vars = {
        l.start.name for l in parfor.loop_nests if isinstance(
            l.start, ir.Var)}
    loop_vars |= {
        l.stop.name for l in parfor.loop_nests if isinstance(
            l.stop, ir.Var)}
    loop_vars |= {
        l.step.name for l in parfor.loop_nests if isinstance(
            l.step, ir.Var)}
    use_set.update(loop_vars)

    return analysis._use_defs_result(usemap=use_set, defmap=def_set)