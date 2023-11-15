def remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map, typemap):
    """create a dummy function from parfor and call remove dead recursively
    """
    blocks = parfor.loop_body.copy()  # shallow copy is enough
    first_body_block = min(blocks.keys())
    assert first_body_block > 0  # we are using 0 for init block here
    last_label = max(blocks.keys())
    return_label = last_label + 1

    loc = blocks[last_label].loc
    scope = blocks[last_label].scope
    blocks[return_label] = ir.Block(scope, loc)

    # add dummy jump in init_block for CFG to work
    blocks[0] = parfor.init_block
    blocks[0].body.append(ir.Jump(first_body_block, loc))

    # add lives in a dummpy return to last block to avoid their removal
    tuple_var = ir.Var(scope, mk_unique_var("$tuple_var"), loc)
    # dummy type for tuple_var
    typemap[tuple_var.name] = types.containers.UniTuple(
        types.intp, 2)
    live_vars = [ir.Var(scope, v, loc) for v in lives]
    tuple_call = ir.Expr.build_tuple(live_vars, loc)
    blocks[return_label].body.append(ir.Assign(tuple_call, tuple_var, loc))
    blocks[return_label].body.append(ir.Return(tuple_var, loc))

    branch = ir.Branch(0, first_body_block, return_label, loc)
    blocks[last_label].body.append(branch)

    # args var including aliases is ok
    remove_dead(blocks, arg_aliases, typemap, alias_map, arg_aliases)
    typemap.pop(tuple_var.name)  # remove dummy tuple type
    blocks[0].body.pop()  # remove dummy jump
    blocks[last_label].body.pop()  # remove branch
    return