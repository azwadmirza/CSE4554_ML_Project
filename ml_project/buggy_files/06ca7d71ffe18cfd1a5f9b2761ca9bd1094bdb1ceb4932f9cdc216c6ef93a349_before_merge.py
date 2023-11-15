def _extract_axis(data, axis=0, intersect=False):
    from pandas.core.index import _union_indexes

    if len(data) == 0:
        index = Index([])
    elif len(data) > 0:
        raw_lengths = []
        indexes = []

        have_raw_arrays = False
        have_frames = False

        for v in data.values():
            if isinstance(v, DataFrame):
                have_frames = True
                indexes.append(v._get_axis(axis))
            else:
                have_raw_arrays = True
                raw_lengths.append(v.shape[axis])

        if have_frames:
            index = _get_combined_index(indexes, intersect=intersect)

        if have_raw_arrays:
            lengths = list(set(raw_lengths))
            if len(lengths) > 1:
                raise ValueError('ndarrays must match shape on axis %d' % axis)

            if have_frames:
                assert(lengths[0] == len(index))
            else:
                index = Index(np.arange(lengths[0]))

    return _ensure_index(index)