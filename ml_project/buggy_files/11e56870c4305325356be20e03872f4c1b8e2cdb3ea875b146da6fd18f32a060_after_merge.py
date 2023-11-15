def remove_dead_parfor(parfor, lives, arg_aliases, alias_map, typemap):
    # remove dead get/sets in last block
    # FIXME: I think that "in the last block" is not sufficient in general.  We might need to
    # remove from any block.
    last_label = max(parfor.loop_body.keys())
    last_block = parfor.loop_body[last_label]

    # save array values set to replace getitems
    saved_values = {}
    new_body = []
    for stmt in last_block.body:
        if (isinstance(stmt, ir.SetItem) and stmt.index.name ==
                parfor.index_var.name and stmt.target.name not in lives):
            saved_values[stmt.target.name] = stmt.value
        if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
            rhs = stmt.value
            if rhs.op == 'getitem' and rhs.index.name == parfor.index_var.name:
                # replace getitem if value saved
                stmt.value = saved_values.get(rhs.value.name, rhs)
        new_body.append(stmt)
    last_block.body = new_body

    alias_set = set(alias_map.keys())
    # after getitem replacement, remove extra setitems
    new_body = []
    in_lives = copy.copy(lives)
    for stmt in reversed(last_block.body):
        # aliases of lives are also live for setitems
        alias_lives = in_lives & alias_set
        for v in alias_lives:
            in_lives |= alias_map[v]
        if (isinstance(stmt, ir.SetItem) and stmt.index.name ==
                parfor.index_var.name and stmt.target.name not in in_lives):
            continue
        in_lives |= {v.name for v in stmt.list_vars()}
        new_body.append(stmt)
    new_body.reverse()
    last_block.body = new_body

    # process parfor body recursively
    remove_dead_parfor_recursive(parfor, lives, arg_aliases, alias_map, typemap)
    return