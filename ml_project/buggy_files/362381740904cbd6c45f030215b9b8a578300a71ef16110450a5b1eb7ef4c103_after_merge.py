def _inline_arraycall(func_ir, cfg, visited, loop, swapped, enable_prange=False,
                      typed=False):
    """Look for array(list) call in the exit block of a given loop, and turn list operations into
    array operations in the loop if the following conditions are met:
      1. The exit block contains an array call on the list;
      2. The list variable is no longer live after array call;
      3. The list is created in the loop entry block;
      4. The loop is created from an range iterator whose length is known prior to the loop;
      5. There is only one list_append operation on the list variable in the loop body;
      6. The block that contains list_append dominates the loop head, which ensures list
         length is the same as loop length;
    If any condition check fails, no modification will be made to the incoming IR.
    """
    debug_print = _make_debug_print("inline_arraycall")
    # There should only be one loop exit
    require(len(loop.exits) == 1)
    exit_block = next(iter(loop.exits))
    list_var, array_call_index, array_kws = _find_arraycall(func_ir, func_ir.blocks[exit_block])

    # check if dtype is present in array call
    dtype_def = None
    dtype_mod_def = None
    if 'dtype' in array_kws:
        require(isinstance(array_kws['dtype'], ir.Var))
        # We require that dtype argument to be a constant of getattr Expr, and we'll
        # remember its definition for later use.
        dtype_def = get_definition(func_ir, array_kws['dtype'])
        require(isinstance(dtype_def, ir.Expr) and dtype_def.op == 'getattr')
        dtype_mod_def = get_definition(func_ir, dtype_def.value)

    list_var_def = get_definition(func_ir, list_var)
    debug_print("list_var = ", list_var, " def = ", list_var_def)
    if isinstance(list_var_def, ir.Expr) and list_var_def.op == 'cast':
        list_var_def = get_definition(func_ir, list_var_def.value)
    # Check if the definition is a build_list
    require(isinstance(list_var_def, ir.Expr) and list_var_def.op ==  'build_list')

    # Look for list_append in "last" block in loop body, which should be a block that is
    # a post-dominator of the loop header.
    list_append_stmts = []
    for label in loop.body:
        # We have to consider blocks of this loop, but not sub-loops.
        # To achieve this, we require the set of "in_loops" of "label" to be visited loops.
        in_visited_loops = [l.header in visited for l in cfg.in_loops(label)]
        if not all(in_visited_loops):
            continue
        block = func_ir.blocks[label]
        debug_print("check loop body block ", label)
        for stmt in block.find_insts(ir.Assign):
            lhs = stmt.target
            expr = stmt.value
            if isinstance(expr, ir.Expr) and expr.op == 'call':
                func_def = get_definition(func_ir, expr.func)
                if isinstance(func_def, ir.Expr) and func_def.op == 'getattr' \
                  and func_def.attr == 'append':
                    list_def = get_definition(func_ir, func_def.value)
                    debug_print("list_def = ", list_def, list_def == list_var_def)
                    if list_def == list_var_def:
                        # found matching append call
                        list_append_stmts.append((label, block, stmt))

    # Require only one list_append, otherwise we won't know the indices
    require(len(list_append_stmts) == 1)
    append_block_label, append_block, append_stmt = list_append_stmts[0]

    # Check if append_block (besides loop entry) dominates loop header.
    # Since CFG doesn't give us this info without loop entry, we approximate
    # by checking if the predecessor set of the header block is the same
    # as loop_entries plus append_block, which is certainly more restrictive
    # than necessary, and can be relaxed if needed.
    preds = set(l for l, b in cfg.predecessors(loop.header))
    debug_print("preds = ", preds, (loop.entries | set([append_block_label])))
    require(preds == (loop.entries | set([append_block_label])))

    # Find iterator in loop header
    iter_vars = []
    iter_first_vars = []
    loop_header = func_ir.blocks[loop.header]
    for stmt in loop_header.find_insts(ir.Assign):
        expr = stmt.value
        if isinstance(expr, ir.Expr):
            if expr.op == 'iternext':
                iter_def = get_definition(func_ir, expr.value)
                debug_print("iter_def = ", iter_def)
                iter_vars.append(expr.value)
            elif expr.op == 'pair_first':
                iter_first_vars.append(stmt.target)

    # Require only one iterator in loop header
    require(len(iter_vars) == 1 and len(iter_first_vars) == 1)
    iter_var = iter_vars[0] # variable that holds the iterator object
    iter_first_var = iter_first_vars[0] # variable that holds the value out of iterator

    # Final requirement: only one loop entry, and we're going to modify it by:
    # 1. replacing the list definition with an array definition;
    # 2. adding a counter for the array iteration.
    require(len(loop.entries) == 1)
    loop_entry = func_ir.blocks[next(iter(loop.entries))]
    terminator = loop_entry.terminator
    scope = loop_entry.scope
    loc = loop_entry.loc
    stmts = []
    removed = []
    def is_removed(val, removed):
        if isinstance(val, ir.Var):
            for x in removed:
                if x.name == val.name:
                    return True
        return False
    # Skip list construction and skip terminator, add the rest to stmts
    for i in range(len(loop_entry.body) - 1):
        stmt = loop_entry.body[i]
        if isinstance(stmt, ir.Assign) and (stmt.value == list_def or is_removed(stmt.value, removed)):
            removed.append(stmt.target)
        else:
            stmts.append(stmt)
    debug_print("removed variables: ", removed)

    # Define an index_var to index the array.
    # If the range happens to be single step ranges like range(n), or range(m, n),
    # then the index_var correlates to iterator index; otherwise we'll have to
    # define a new counter.
    range_def = guard(_find_iter_range, func_ir, iter_var, swapped)
    index_var = ir.Var(scope, mk_unique_var("index"), loc)
    if range_def and range_def[0] == 0:
        # iterator starts with 0, index_var can just be iter_first_var
        index_var = iter_first_var
    else:
        # index_var = -1 # starting the index with -1 since it will incremented in loop header
        stmts.append(_new_definition(func_ir, index_var, ir.Const(value=-1, loc=loc), loc))

    # Insert statement to get the size of the loop iterator
    size_var = ir.Var(scope, mk_unique_var("size"), loc)
    if range_def:
        start, stop, range_func_def = range_def
        if start == 0:
            size_val = stop
        else:
            size_val = ir.Expr.binop(fn=operator.sub, lhs=stop, rhs=start, loc=loc)
        # we can parallelize this loop if enable_prange = True, by changing
        # range function from range, to prange.
        if enable_prange and isinstance(range_func_def, ir.Global):
            range_func_def.name = 'internal_prange'
            range_func_def.value = internal_prange

    else:
        # this doesn't work in objmode as it's effectively untyped
        if typed:
            len_func_var = ir.Var(scope, mk_unique_var("len_func"), loc)
            stmts.append(_new_definition(func_ir, len_func_var,
                        ir.Global('range_iter_len', range_iter_len, loc=loc),
                        loc))
            size_val = ir.Expr.call(len_func_var, (iter_var,), (), loc=loc)
        else:
            raise GuardException


    stmts.append(_new_definition(func_ir, size_var, size_val, loc))

    size_tuple_var = ir.Var(scope, mk_unique_var("size_tuple"), loc)
    stmts.append(_new_definition(func_ir, size_tuple_var,
                 ir.Expr.build_tuple(items=[size_var], loc=loc), loc))

    # Insert array allocation
    array_var = ir.Var(scope, mk_unique_var("array"), loc)
    empty_func = ir.Var(scope, mk_unique_var("empty_func"), loc)
    if dtype_def and dtype_mod_def:
        # when dtype is present, we'll call emtpy with dtype
        dtype_mod_var = ir.Var(scope, mk_unique_var("dtype_mod"), loc)
        dtype_var = ir.Var(scope, mk_unique_var("dtype"), loc)
        stmts.append(_new_definition(func_ir, dtype_mod_var, dtype_mod_def, loc))
        stmts.append(_new_definition(func_ir, dtype_var,
                         ir.Expr.getattr(dtype_mod_var, dtype_def.attr, loc), loc))
        stmts.append(_new_definition(func_ir, empty_func,
                         ir.Global('empty', np.empty, loc=loc), loc))
        array_kws = [('dtype', dtype_var)]
    else:
        # this doesn't work in objmode as it's effectively untyped
        if typed:
            # otherwise we'll call unsafe_empty_inferred
            stmts.append(_new_definition(func_ir, empty_func,
                            ir.Global('unsafe_empty_inferred',
                                unsafe_empty_inferred, loc=loc), loc))
            array_kws = []
        else:
            raise GuardException

    # array_var = empty_func(size_tuple_var)
    stmts.append(_new_definition(func_ir, array_var,
                 ir.Expr.call(empty_func, (size_tuple_var,), list(array_kws), loc=loc), loc))

    # Add back removed just in case they are used by something else
    for var in removed:
        stmts.append(_new_definition(func_ir, var, array_var, loc))

    # Add back terminator
    stmts.append(terminator)
    # Modify loop_entry
    loop_entry.body = stmts

    if range_def:
        if range_def[0] != 0:
            # when range doesn't start from 0, index_var becomes loop index
            # (iter_first_var) minus an offset (range_def[0])
            terminator = loop_header.terminator
            assert(isinstance(terminator, ir.Branch))
            # find the block in the loop body that header jumps to
            block_id = terminator.truebr
            blk = func_ir.blocks[block_id]
            loc = blk.loc
            blk.body.insert(0, _new_definition(func_ir, index_var,
                ir.Expr.binop(fn=operator.sub, lhs=iter_first_var,
                                      rhs=range_def[0], loc=loc),
                loc))
    else:
        # Insert index_var increment to the end of loop header
        loc = loop_header.loc
        terminator = loop_header.terminator
        stmts = loop_header.body[0:-1]
        next_index_var = ir.Var(scope, mk_unique_var("next_index"), loc)
        one = ir.Var(scope, mk_unique_var("one"), loc)
        # one = 1
        stmts.append(_new_definition(func_ir, one,
                     ir.Const(value=1,loc=loc), loc))
        # next_index_var = index_var + 1
        stmts.append(_new_definition(func_ir, next_index_var,
                     ir.Expr.binop(fn=operator.add, lhs=index_var, rhs=one, loc=loc), loc))
        # index_var = next_index_var
        stmts.append(_new_definition(func_ir, index_var, next_index_var, loc))
        stmts.append(terminator)
        loop_header.body = stmts

    # In append_block, change list_append into array assign
    for i in range(len(append_block.body)):
        if append_block.body[i] == append_stmt:
            debug_print("Replace append with SetItem")
            append_block.body[i] = ir.SetItem(target=array_var, index=index_var,
                                              value=append_stmt.value.args[0], loc=append_stmt.loc)

    # replace array call, by changing "a = array(b)" to "a = b"
    stmt = func_ir.blocks[exit_block].body[array_call_index]
    # stmt can be either array call or SetItem, we only replace array call
    if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Expr):
        stmt.value = array_var
        func_ir._definitions[stmt.target.name] = [stmt.value]

    return True