def _loop_lift_modify_blocks(func_ir, loopinfo, blocks,
                             typingctx, targetctx, flags, locals):
    """
    Modify the block inplace to call to the lifted-loop.
    Returns a dictionary of blocks of the lifted-loop.
    """
    from numba.dispatcher import LiftedLoop

    # Copy loop blocks
    loop = loopinfo.loop

    loopblockkeys = set(loop.body) | set(loop.entries)
    if len(loop.exits) > 1:
        # Pre-Py3.8 may have multiple exits
        loopblockkeys |= loop.exits
    loopblocks = dict((k, blocks[k].copy()) for k in loopblockkeys)
    # Modify the loop blocks
    _loop_lift_prepare_loop_func(loopinfo, loopblocks)

    # Create a new IR for the lifted loop
    lifted_ir = func_ir.derive(blocks=loopblocks,
                               arg_names=tuple(loopinfo.inputs),
                               arg_count=len(loopinfo.inputs),
                               force_non_generator=True)
    liftedloop = LiftedLoop(lifted_ir,
                            typingctx, targetctx, flags, locals)

    # modify for calling into liftedloop
    callblock = _loop_lift_modify_call_block(liftedloop, blocks[loopinfo.callfrom],
                                             loopinfo.inputs, loopinfo.outputs,
                                             loopinfo.returnto)
    # remove blocks
    for k in loopblockkeys:
        del blocks[k]
    # update main interpreter callsite into the liftedloop
    blocks[loopinfo.callfrom] = callblock
    return liftedloop