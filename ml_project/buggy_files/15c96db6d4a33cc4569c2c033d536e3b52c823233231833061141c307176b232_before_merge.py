def copy_propagate_update_analysis(stmt, var_dict, array_analysis):
    """update array analysis data during copy propagation.
    If an array is in defs of a statement, we update its size variables.
    """
    array_shape_classes = array_analysis.array_shape_classes
    class_sizes = array_analysis.class_sizes
    array_size_vars = array_analysis.array_size_vars
    # find defs of stmt
    def_set = set()
    if isinstance(stmt, ir.Assign):
        def_set.add(stmt.target.name)
    for T, def_func in analysis.ir_extension_defs.items():
        if isinstance(stmt, T):
            def_set = def_func(stmt)
    # update analysis for arrays in defs
    for var in def_set:
        if var in array_shape_classes:
            if var in array_size_vars:
                array_size_vars[var] = replace_vars_inner(array_size_vars[var],
                    var_dict)
            shape_corrs = array_shape_classes[var]
            for c in shape_corrs:
                if c!=-1:
                    class_sizes[c] = replace_vars_inner(class_sizes[c], var_dict)
    return