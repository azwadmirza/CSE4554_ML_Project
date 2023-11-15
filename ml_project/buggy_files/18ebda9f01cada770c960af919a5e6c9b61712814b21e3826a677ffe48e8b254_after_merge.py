def unwrap_parfor_blocks(parfor, blocks=None):
    """
    unwrap parfor blocks after analysis/optimization.
    Allows changes to the parfor loop.
    """
    if blocks is not None:
        # make sure init block isn't removed
        assert 0 in blocks
        # update loop body blocks
        blocks.pop(0)
        parfor.loop_body = blocks

    # make sure dummy jump to loop body isn't altered
    first_body_label = min(parfor.loop_body.keys())
    assert isinstance(parfor.init_block.body[-1], ir.Jump)
    assert parfor.init_block.body[-1].target == first_body_label

    # remove dummy jump to loop body
    parfor.init_block.body.pop()

    # make sure dummy jump back to loop body isn't altered
    last_label = max(parfor.loop_body.keys())
    assert isinstance(parfor.loop_body[last_label].body[-1], ir.Jump)
    assert parfor.loop_body[last_label].body[-1].target == first_body_label
    # remove dummy jump back to loop
    parfor.loop_body[last_label].body.pop()
    return