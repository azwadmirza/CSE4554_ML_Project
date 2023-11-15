def remove_dead_parfor_recursive(parfor, lives, args):
    """create a dummy function from parfor and call remove dead recursively
    """
    blocks = parfor.loop_body.copy() # shallow copy is enough
    first_body_block = min(blocks.keys())
    assert first_body_block > 0 # we are using 0 for init block here
    last_label = max(blocks.keys())
    if len(blocks[last_label].body) == 0:
        return
    loc = blocks[last_label].body[-1].loc
    scope = blocks[last_label].scope

    # add dummy jump in init_block for CFG to work
    blocks[0] = parfor.init_block
    blocks[0].body.append(ir.Jump(first_body_block, loc))
    # add lives in a dummpy return to last block to avoid their removal
    tuple_var = ir.Var(scope, mk_unique_var("$tuple_var"), loc)
    live_vars = [ ir.Var(scope,v,loc) for v in lives ]
    tuple_call = ir.Expr.build_tuple(live_vars, loc)
    blocks[last_label].body.append(ir.Assign(tuple_call, tuple_var, loc))
    blocks[last_label].body.append(ir.Return(tuple_var,loc))
    remove_dead(blocks, args)
    blocks[0].body.pop() # remove dummy jump
    blocks[last_label].body.pop() # remove dummy return
    blocks[last_label].body.pop() # remove dummy tupple
    return