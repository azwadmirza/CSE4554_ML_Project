def remove_dead_parfor(parfor, lives, args):
    # remove dead get/sets in last block
    # FIXME: I think that "in the last block" is not sufficient in general.  We might need to
    # remove from any block.
    last_label = max(parfor.loop_body.keys())
    last_block = parfor.loop_body[last_label]

    # save array values set to replace getitems
    saved_values = {}
    new_body = []
    for stmt in last_block.body:
        if (isinstance(stmt, ir.SetItem) and stmt.index.name==parfor.index_var.name
                and stmt.target.name not in lives):
            saved_values[stmt.target.name] = stmt.value
        if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
            rhs = stmt.value
            if rhs.op=='getitem' and rhs.index.name==parfor.index_var.name:
                # replace getitem if value saved
                stmt.value = saved_values.get(rhs.value.name, rhs)
        new_body.append(stmt)
    last_block.body = new_body
    # process parfor body recursively
    remove_dead_parfor_recursive(parfor, lives, args)
    return