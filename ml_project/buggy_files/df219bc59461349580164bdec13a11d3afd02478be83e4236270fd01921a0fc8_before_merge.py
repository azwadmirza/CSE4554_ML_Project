def _extract_loop_lifting_candidates(cfg, blocks):
    """
    Returns a list of loops that are candidate for loop lifting
    """
    # check well-formed-ness of the loop
    def same_exit_point(loop):
        "all exits must point to the same location"
        outedges = set()
        for k in loop.exits:
            outedges |= set(x for x, _ in cfg.successors(k))
        return len(outedges) == 1

    def one_entry(loop):
        "there is one entry"
        return len(loop.entries) == 1

    def cannot_yield(loop):
        "cannot have yield inside the loop"
        insiders = set(loop.body) | set(loop.entries) | set(loop.exits)
        for blk in map(blocks.__getitem__, insiders):
            for inst in blk.body:
                if isinstance(inst, ir.Assign):
                    if isinstance(inst.value, ir.Yield):
                        return False
        return True

    return [loop for loop in find_top_level_loops(cfg)
            if same_exit_point(loop) and one_entry(loop) and cannot_yield(loop)]