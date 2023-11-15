def _loop_lift_get_candidate_infos(cfg, blocks, livemap):
    """
    Returns information on looplifting candidates.
    """
    loops = _extract_loop_lifting_candidates(cfg, blocks)
    loopinfos = []
    for loop in loops:

        [callfrom] = loop.entries   # requirement checked earlier
        an_exit = next(iter(loop.exits))  # anyone of the exit block
        if len(loop.exits) > 1:
            # Pre-Py3.8 may have multiple exits
            [(returnto, _)] = cfg.successors(an_exit)  # requirement checked earlier
        else:
            # Post-Py3.8 DO NOT have multiple exits
            returnto = an_exit

        local_block_ids = set(loop.body) | set(loop.entries)
        inputs, outputs = find_region_inout_vars(
            blocks=blocks,
            livemap=livemap,
            callfrom=callfrom,
            returnto=returnto,
            body_block_ids=local_block_ids,
        )

        lli = _loop_lift_info(loop=loop, inputs=inputs, outputs=outputs,
                              callfrom=callfrom, returnto=returnto)
        loopinfos.append(lli)

    return loopinfos