def deep_align(list_of_variable_maps, join='outer', copy=True, indexes=None,
               skip_single_target=False):
    """Align objects, recursing into dictionary values.
    """
    if indexes is None:
        indexes = {}

    # We use keys to identify arguments to align. Integers indicate single
    # arguments, while (int, variable_name) pairs indicate variables in ordered
    # dictionaries.
    keys = []
    out = []
    targets = []
    sentinel = object()
    for n, variables in enumerate(list_of_variable_maps):
        if is_alignable(variables):
            keys.append(n)
            targets.append(variables)
            out.append(sentinel)
        elif is_dict_like(variables):
            for k, v in variables.items():
                if is_alignable(v) and k not in indexes:
                    # don't align dict-like variables that are already fixed
                    # indexes: we might be overwriting these index variables
                    keys.append((n, k))
                    targets.append(v)
            out.append(OrderedDict(variables))
        else:
            out.append(variables)

    aligned = partial_align(*targets, join=join, copy=copy, indexes=indexes,
                            skip_single_target=skip_single_target)

    for key, aligned_obj in zip(keys, aligned):
        if isinstance(key, tuple):
            n, k = key
            out[n][k] = aligned_obj
        else:
            out[key] = aligned_obj

    # something went wrong: we should have replaced all sentinel values
    assert all(arg is not sentinel for arg in out)

    return out