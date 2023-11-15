def _get_saved_call_nodes(fname, saved_globals, saved_getattrs, block_defs):
    nodes = []
    while (fname not in block_defs and (fname in saved_globals
                                        or fname in saved_getattrs)):
        if fname in saved_globals:
            nodes.append(saved_globals[fname])
            block_defs.add(saved_globals[fname].target.name)
            fname = '_PA_DONE'
        elif fname in saved_getattrs:
            up_name = saved_getattrs[fname].value.value.name
            nodes.append(saved_getattrs[fname])
            block_defs.add(saved_getattrs[fname].target.name)
            fname = up_name
    nodes.reverse()
    return nodes