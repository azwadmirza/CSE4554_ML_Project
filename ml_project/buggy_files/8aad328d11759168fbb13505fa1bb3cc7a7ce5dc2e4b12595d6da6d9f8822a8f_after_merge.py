def maximize_fusion(blocks):
    call_table, _ = get_call_table(blocks)
    for block in blocks.values():
        order_changed = True
        while order_changed:
            order_changed = False
            i = 0
            while i < len(block.body) - 2:
                stmt = block.body[i]
                next_stmt = block.body[i + 1]
                # swap only parfors with non-parfors
                # don't reorder calls with side effects (e.g. file close)
                # only read-read dependencies are OK
                # make sure there is no write-write, write-read dependencies
                if (isinstance(
                        stmt, Parfor) and not isinstance(
                        next_stmt, Parfor)
                        and (not isinstance(next_stmt, ir.Assign)
                             or has_no_side_effect(
                            next_stmt.value, set(), call_table))):
                    stmt_accesses = {v.name for v in stmt.list_vars()}
                    stmt_writes = get_parfor_writes(stmt)
                    next_accesses = {v.name for v in next_stmt.list_vars()}
                    next_writes = get_stmt_writes(next_stmt)
                    if len((stmt_writes & next_accesses)
                            | (next_writes & stmt_accesses)) == 0:
                        block.body[i] = next_stmt
                        block.body[i + 1] = stmt
                        order_changed = True
                i += 1
    return