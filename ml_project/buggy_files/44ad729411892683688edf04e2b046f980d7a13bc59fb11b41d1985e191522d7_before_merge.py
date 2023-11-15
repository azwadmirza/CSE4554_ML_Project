def remove_dead_block(block, lives, call_table, args):
    """remove dead code using liveness info.
    Mutable arguments (e.g. arrays) that are not definitely assigned are live
    after return of function.
    """
    # TODO: find mutable args that are not definitely assigned instead of
    # assuming all args are live after return
    removed = False

    # add statements in reverse order
    new_body = [block.terminator]
    # for each statement in reverse order, excluding terminator
    for stmt in reversed(block.body[:-1]):
        # let external calls handle stmt if type matches
        for t,f in remove_dead_extensions.items():
            if isinstance(stmt,t):
                f(stmt, lives, args)
        # ignore assignments that their lhs is not live or lhs==rhs
        if isinstance(stmt, ir.Assign):
            lhs = stmt.target
            rhs = stmt.value
            if lhs.name not in lives and has_no_side_effect(rhs, lives, call_table):
                removed = True
                continue
            if isinstance(rhs, ir.Var) and lhs.name==rhs.name:
                removed = True
                continue
            # TODO: remove other nodes like SetItem etc.
        if isinstance(stmt, ir.SetItem):
            if stmt.target.name not in lives:
                continue

        lives |= { v.name for v in stmt.list_vars() }
        if isinstance(stmt, ir.Assign):
            lives.remove(lhs.name)
        for T, def_func in analysis.ir_extension_defs.items():
            if isinstance(stmt, T):
                lives -= def_func(stmt)
        new_body.append(stmt)
    new_body.reverse()
    block.body = new_body
    return removed