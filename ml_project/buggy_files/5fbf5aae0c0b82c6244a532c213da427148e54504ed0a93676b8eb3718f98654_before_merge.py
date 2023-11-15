def unify_nsplits(*tensor_axes):
    from .rechunk import rechunk

    tensor_splits = [dict((a, split) for a, split in izip(axes, t.nsplits) if split != (1,))
                     for t, axes in tensor_axes]
    common_axes = reduce(operator.and_, [set(lkeys(ts)) for ts in tensor_splits])
    axes_unified_splits = dict((ax, decide_unify_split(*(t[ax] for t in tensor_splits)))
                               for ax in common_axes)

    if len(common_axes) == 0:
        return tuple(t[0] for t in tensor_axes)

    res = []
    for t, axes in tensor_axes:
        new_chunk = dict((i, axes_unified_splits[ax]) for ax, i in zip(axes, range(t.ndim))
                         if ax in axes_unified_splits)
        res.append(rechunk(t, new_chunk).single_tiles())

    return tuple(res)