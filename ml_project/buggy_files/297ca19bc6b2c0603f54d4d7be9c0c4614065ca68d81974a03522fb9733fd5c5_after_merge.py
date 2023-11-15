def _loop_lift_get_candidate_infos(cfg, blocks, livemap):
    """
    Returns information on looplifting candidates.
    """
    loops = _extract_loop_lifting_candidates(cfg, blocks)
    loopinfos = []
    for loop in loops:
        [callfrom] = loop.entries   # requirement checked earlier
        # This loop exists to handle missing cfg.successors, only *an* exit is
        # needed. Walk in stable order, higher exits first.
        for an_exit in iter(sorted(loop.exits)):
            # requirement checked earlier
            ret = [x for x in cfg.successors(an_exit)]
            if ret:
                break
        else:
            continue # drop this loop from being liftable 
        [(returnto, _)] = ret
        # note: sorted for stable ordering
        inputs = sorted(livemap[callfrom])
        outputs = sorted(livemap[returnto])
        lli = _loop_lift_info(loop=loop, inputs=inputs, outputs=outputs,
                              callfrom=callfrom, returnto=returnto)
        loopinfos.append(lli)
    return loopinfos