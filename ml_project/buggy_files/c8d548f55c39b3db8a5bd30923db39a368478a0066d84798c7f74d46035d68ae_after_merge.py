def _get_saved_call_nodes(fname, saved_globals, saved_getattrs, block_defs, rename_dict):
    """ Implement the copying of globals or getattrs for the purposes noted in
        push_call_vars.  We make a new var and assign to it a copy of the
        global or getattr.  We remember this new assignment node and add an
        entry in the renaming dictionary so that for this block the original
        var name is replaced by the new var name we created.
    """
    nodes = []
    while (fname not in block_defs and (fname in saved_globals
                                        or fname in saved_getattrs)):
        def rename_global_or_getattr(obj, var_base, nodes, block_defs, rename_dict):
            assert(isinstance(obj, ir.Assign))
            renamed_var = ir.Var(obj.target.scope,
                                 mk_unique_var(var_base),
                                 obj.target.loc)
            renamed_assign = ir.Assign(copy.deepcopy(obj.value),
                                       renamed_var,
                                       obj.loc)
            nodes.append(renamed_assign)
            block_defs.add(obj.target.name)
            rename_dict[obj.target.name] = renamed_assign.target.name

        if fname in saved_globals:
            rename_global_or_getattr(saved_globals[fname], "$push_global_to_block",
                                     nodes, block_defs, rename_dict)
            fname = '_PA_DONE'
        elif fname in saved_getattrs:
            rename_global_or_getattr(saved_getattrs[fname], "$push_getattr_to_block",
                                     nodes, block_defs, rename_dict)
            fname = saved_getattrs[fname].value.value.name
    nodes.reverse()
    return nodes