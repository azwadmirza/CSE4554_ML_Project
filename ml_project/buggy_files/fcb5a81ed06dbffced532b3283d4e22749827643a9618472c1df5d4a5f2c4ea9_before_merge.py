def _extract_loop_lifting_candidates(cfg, blocks):
    """
    Returns a list of loops that are candidate for loop lifting
    """
    # check well-formed-ness of the loop
    def same_exit_point(loop):
        "all exits must point to the same location"
        outedges = set()
        for k in loop.exits:
            succs = set(x for x, _ in cfg.successors(k))
            if not succs:
                # If the exit point has no successor, it contains an return
                # statement, which is not handled by the looplifting code.
                # Thus, this loop is not a candidate.
                _logger.debug("return-statement in loop.")
                return False
            outedges |= succs
        ok = len(outedges) == 1
        _logger.debug("same_exit_point=%s", ok)
        return ok

    def one_entry(loop):
        "there is one entry"
        ok = len(loop.entries) == 1
        _logger.debug("one_entry=%s", ok)
        return ok

    def cannot_yield(loop):
        "cannot have yield inside the loop"
        insiders = set(loop.body) | set(loop.entries) | set(loop.exits)
        for blk in map(blocks.__getitem__, insiders):
            for inst in blk.body:
                if isinstance(inst, ir.Assign):
                    if isinstance(inst.value, ir.Yield):
                        _logger.debug("has yield")
                        return False
        _logger.debug("no yield")
        return True

    _logger.info('finding looplift candidates')
    # the check for cfg.entry_point in the loop.entries is to prevent a bad
    # rewrite where a prelude for a lifted loop would get written into block -1
    # if a loop entry were in block 0
    candidates = []
    for loop in find_top_level_loops(cfg):
        _logger.debug("top-level loop: %s", loop)
        if (same_exit_point(loop) and one_entry(loop) and cannot_yield(loop) and
            cfg.entry_point() not in loop.entries):
            candidates.append(loop)
            _logger.debug("add candidate: %s", loop)
    return candidates