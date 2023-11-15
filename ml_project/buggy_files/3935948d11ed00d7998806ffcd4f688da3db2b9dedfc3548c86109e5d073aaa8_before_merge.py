def apply_copy_propagate(blocks, in_copies, name_var_table, ext_func, ext_data,
        typemap, calltypes):
    """apply copy propagation to IR: replace variables when copies available"""
    for label, block in blocks.items():
        var_dict = {l:name_var_table[r] for l,r in in_copies[label]}
        # assignments as dict to replace with latest value
        for stmt in block.body:
            ext_func(stmt, var_dict, ext_data)
            for T,f in apply_copy_propagate_extensions.items():
                if isinstance(stmt,T):
                    f(stmt, var_dict, name_var_table, ext_func, ext_data,
                        typemap, calltypes)
            # only rhs of assignments should be replaced
            # e.g. if x=y is available, x in x=z shouldn't be replaced
            if isinstance(stmt, ir.Assign):
                stmt.value = replace_vars_inner(stmt.value, var_dict)
            else:
                replace_vars_stmt(stmt, var_dict)
            fix_setitem_type(stmt, typemap, calltypes)
            for T,f in copy_propagate_extensions.items():
                if isinstance(stmt,T):
                    gen_set, kill_set = f(stmt, typemap)
                    for lhs,rhs in gen_set:
                        var_dict[lhs] = name_var_table[rhs]
                    for l,r in var_dict.copy().items():
                        if l in kill_set or r.name in kill_set:
                            var_dict.pop(l)
            if isinstance(stmt, ir.Assign) and isinstance(stmt.value, ir.Var):
                lhs = stmt.target.name
                rhs = stmt.value.name
                # rhs could be replaced with lhs from previous copies
                if lhs!=rhs:
                    # copy is valid only if same type (see TestCFunc.test_locals)
                    if typemap[lhs]==typemap[rhs]:
                        var_dict[lhs] = name_var_table[rhs]
                    else:
                        var_dict.pop(lhs, None)
                    # a=b kills previous t=a
                    lhs_kill = []
                    for k,v in var_dict.items():
                        if v.name==lhs:
                            lhs_kill.append(k)
                    for k in lhs_kill:
                        var_dict.pop(k, None)
    return