def get_block_copies(blocks, typemap):
    """get copies generated and killed by each block
    """
    block_copies = {}
    extra_kill = {}
    for label, block in blocks.items():
        assign_dict = {}
        extra_kill[label] = set()
        # assignments as dict to replace with latest value
        for stmt in block.body:
            for T,f in copy_propagate_extensions.items():
                if isinstance(stmt,T):
                    gen_set, kill_set = f(stmt, typemap)
                    for lhs,rhs in gen_set:
                        assign_dict[lhs] = rhs
                    extra_kill[label] |= kill_set
            if isinstance(stmt, ir.Assign):
                lhs = stmt.target.name
                if isinstance(stmt.value, ir.Var):
                    rhs = stmt.value.name
                    # copy is valid only if same type (see TestCFunc.test_locals)
                    if typemap[lhs]==typemap[rhs]:
                        assign_dict[lhs] = rhs
                        continue
                extra_kill[label].add(lhs)
        block_copies[label] = set(assign_dict.items())
    return block_copies, extra_kill