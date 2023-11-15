def remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map,
                                                             func_ir, typemap):
    """create a dummy function from parfor and call remove dead recursively
    """
    blocks = parfor.loop_body.copy()  # shallow copy is enough
    first_body_block = min(blocks.keys())
    assert first_body_block > 0  # we are using 0 for init block here
    last_label = max(blocks.keys())

    return_label, tuple_var = _add_liveness_return_block(blocks, lives, typemap)

    # branch back to first body label to simulate loop
    branch = ir.Branch(0, first_body_block, return_label, ir.Loc("parfors_dummy", -1))
    blocks[last_label].body.append(branch)

    # add dummy jump in init_block for CFG to work
    blocks[0] = parfor.init_block
    blocks[0].body.append(ir.Jump(first_body_block, ir.Loc("parfors_dummy", -1)))

    # args var including aliases is ok
    remove_dead(blocks, arg_aliases, func_ir, typemap, alias_map, arg_aliases)
    typemap.pop(tuple_var.name)  # remove dummy tuple type
    blocks[0].body.pop()  # remove dummy jump
    blocks[last_label].body.pop()  # remove branch
    return