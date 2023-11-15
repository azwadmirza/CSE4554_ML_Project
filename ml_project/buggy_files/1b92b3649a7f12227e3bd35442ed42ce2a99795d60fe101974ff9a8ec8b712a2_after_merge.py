def align_and_merge_coords(objs, compat='minimal', join='outer',
                           priority_arg=None, indexes=None):
    """Align and merge coordinate variables."""
    _assert_compat_valid(compat)
    coerced = coerce_pandas_values(objs)
    aligned = deep_align(coerced, join=join, copy=False, indexes=indexes,
                         skip_single_target=True)
    expanded = expand_variable_dicts(aligned)
    priority_vars = _get_priority_vars(aligned, priority_arg, compat=compat)
    variables = merge_variables(expanded, priority_vars, compat=compat)

    return variables