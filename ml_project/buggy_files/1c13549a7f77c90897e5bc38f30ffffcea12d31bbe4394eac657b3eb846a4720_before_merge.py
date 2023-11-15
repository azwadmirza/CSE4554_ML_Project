def wrap_parfor_blocks(parfor):
    """wrap parfor blocks for analysis/optimization like CFG"""
    blocks = parfor.loop_body.copy() # shallow copy is enough
    first_body_block = min(blocks.keys())
    assert first_body_block > 0 # we are using 0 for init block here
    last_label = max(blocks.keys())
    loc = blocks[last_label].body[-1].loc

    # add dummy jump in init_block for CFG to work
    blocks[0] = parfor.init_block
    blocks[0].body.append(ir.Jump(first_body_block, loc))
    blocks[last_label].body.append(ir.Jump(first_body_block,loc))
    return blocks