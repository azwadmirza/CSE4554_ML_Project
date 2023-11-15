def push_call_vars(blocks, saved_globals, saved_getattrs, nested=False):
    """push call variables to right before their call site.
    assuming one global/getattr is created for each call site and control flow
    doesn't change it.
    """
    for block in blocks.values():
        new_body = []
        # global/attr variables that are defined in this block already,
        #   no need to reassign them
        block_defs = set()
        for stmt in block.body:
            def process_assign(stmt):
                if isinstance(stmt, ir.Assign):
                    rhs = stmt.value
                    lhs = stmt.target
                    if (isinstance(rhs, ir.Global)):
                        saved_globals[lhs.name] = stmt
                        block_defs.add(lhs.name)
                    elif isinstance(rhs, ir.Expr) and rhs.op == 'getattr':
                        if (rhs.value.name in saved_globals
                                or rhs.value.name in saved_getattrs):
                            saved_getattrs[lhs.name] = stmt
                            block_defs.add(lhs.name)

            if not nested and isinstance(stmt, Parfor):
                for s in stmt.init_block.body:
                    process_assign(s)
                pblocks = stmt.loop_body.copy()
                push_call_vars(pblocks, saved_globals, saved_getattrs, nested=True)
                new_body.append(stmt)
                continue
            else:
                process_assign(stmt)
            for v in stmt.list_vars():
                new_body += _get_saved_call_nodes(v.name, saved_globals,
                                                  saved_getattrs, block_defs)
            new_body.append(stmt)
        block.body = new_body

    return