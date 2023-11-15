def unwrap_parfor_blocks(parfor):
    last_label = max(parfor.loop_body.keys())
    parfor.init_block.body.pop() # remove dummy jump
    parfor.loop_body[last_label].body.pop() # remove dummy return
    return