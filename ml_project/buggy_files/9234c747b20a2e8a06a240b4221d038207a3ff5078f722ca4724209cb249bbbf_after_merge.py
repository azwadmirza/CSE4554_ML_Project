def normalize_array_selection(item, shape):
    """Convenience function to normalize a selection within an array with
    the given `shape`."""

    # ensure tuple
    if not isinstance(item, tuple):
        item = (item,)

    # handle ellipsis
    n_ellipsis = sum(1 for i in item if i == Ellipsis)
    if n_ellipsis > 1:
        raise IndexError("an index can only have a single ellipsis ('...')")
    elif n_ellipsis == 1:
        idx_ellipsis = item.index(Ellipsis)
        n_items_l = idx_ellipsis  # items to left of ellipsis
        n_items_r = len(item) - (idx_ellipsis + 1)  # items to right of ellipsis
        n_items = len(item) - 1  # all non-ellipsis items
        if n_items >= len(shape):
            # ellipsis does nothing, just remove it
            item = tuple(i for i in item if i != Ellipsis)
        else:
            # replace ellipsis with slices
            new_item = item[:n_items_l] + ((slice(None),) * (len(shape) - n_items))
            if n_items_r:
                new_item += item[-n_items_r:]
            item = new_item

    # check dimensionality
    if len(item) > len(shape):
        raise IndexError('too many indices for array')

    # determine start and stop indices for all axes
    selection = tuple(normalize_axis_selection(i, l) for i, l in zip(item, shape))

    # fill out selection if not completely specified
    if len(selection) < len(shape):
        selection += tuple(slice(0, l) for l in shape[len(selection):])

    return selection