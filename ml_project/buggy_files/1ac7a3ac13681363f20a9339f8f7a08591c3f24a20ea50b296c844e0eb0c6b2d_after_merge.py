def merge_core(objs, compat='broadcast_equals', join='outer', priority_arg=None,
               explicit_coords=None, indexes=None):
    """Core logic for merging labeled objects.

    This is not public API.

    Parameters
    ----------
    objs : list of mappings
        All values must be convertable to labeled arrays.
    compat : 'broadcast_equals', 'equals' or 'identical', optional
        Compatibility checks to use when merging variables.
    join : 'outer', 'inner', 'left' or 'right', optional
        How to combine objects with different indexes.
    priority_arg : integer, optional
        Optional argument in `objs` that takes precedence over the others.
    explicit_coords : set, optional
        An explicit list of variables from `objs` that are coordinates.
    indexes : dict, optional
        Dictionary with values given by pandas.Index objects.

    Returns
    -------
    variables : OrderedDict
        Ordered dictionary of Variable objects.
    coord_names : set
        Set of coordinate names.
    dims : dict
        Dictionary mapping from dimension names to sizes.

    Raises
    ------
    MergeError if the merge cannot be done successfully.
    """
    from .dataset import calculate_dimensions

    _assert_compat_valid(compat)

    coerced = coerce_pandas_values(objs)
    aligned = deep_align(coerced, join=join, copy=False, indexes=indexes,
                         skip_single_target=True)
    expanded = expand_variable_dicts(aligned)

    coord_names, noncoord_names = determine_coords(coerced)

    if explicit_coords is not None:
        coord_names.update(explicit_coords)

    priority_vars = _get_priority_vars(aligned, priority_arg, compat=compat)
    variables = merge_variables(expanded, priority_vars, compat=compat)

    dims = calculate_dimensions(variables)

    for dim, size in dims.items():
        if dim not in variables:
            variables[dim] = default_index_coordinate(dim, size)

    coord_names.update(dims)

    ambiguous_coords = coord_names.intersection(noncoord_names)
    if ambiguous_coords:
        raise MergeError('unable to determine if these variables should be '
                         'coordinates or not in the merged result: %s'
                         % ambiguous_coords)

    return variables, coord_names, dict(dims)