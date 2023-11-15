def block2d_to_block3d(values, items, shape, major_labels, minor_labels,
                       ref_items=None):
    """
    Developer method for pivoting DataFrame -> Panel. Used in HDFStore and
    DataFrame.to_panel
    """
    from pandas.core.internals import make_block
    panel_shape = (len(items),) + shape

    # TODO: lexsort depth needs to be 2!!

    # Create observation selection vector using major and minor
    # labels, for converting to panel format.
    selector = minor_labels + shape[1] * major_labels
    mask = np.zeros(np.prod(shape), dtype=bool)
    mask.put(selector, True)

    pvalues = np.empty(panel_shape, dtype=values.dtype)
    if not issubclass(pvalues.dtype.type, (np.integer, np.bool_)):
        pvalues.fill(np.nan)
    elif not mask.all():
        pvalues = com._maybe_upcast(pvalues)
        pvalues.fill(np.nan)

    values = values
    for i in xrange(len(items)):
        pvalues[i].flat[mask] = values[:, i]

    if ref_items is None:
        ref_items = items

    return make_block(pvalues, items, ref_items)