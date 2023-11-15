def _bins_to_cuts(x, bins, right=True, labels=None,
                  precision=3, include_lowest=False,
                  dtype=None, duplicates='raise'):

    if duplicates not in ['raise', 'drop']:
        raise ValueError("invalid value for 'duplicates' parameter, "
                         "valid options are: raise, drop")

    unique_bins = algos.unique(bins)
    if len(unique_bins) < len(bins):
        if duplicates == 'raise':
            raise ValueError("Bin edges must be unique: {}.\nYou "
                             "can drop duplicate edges by setting "
                             "the 'duplicates' kwarg".format(repr(bins)))
        else:
            bins = unique_bins

    side = 'left' if right else 'right'
    ids = bins.searchsorted(x, side=side)

    if include_lowest:
        ids[x == bins[0]] = 1

    na_mask = isnull(x) | (ids == len(bins)) | (ids == 0)
    has_nas = na_mask.any()

    if labels is not False:
        if labels is None:
            increases = 0
            while True:
                try:
                    levels = _format_levels(bins, precision, right=right,
                                            include_lowest=include_lowest,
                                            dtype=dtype)
                except ValueError:
                    increases += 1
                    precision += 1
                    if increases >= 20:
                        raise
                else:
                    break

        else:
            if len(labels) != len(bins) - 1:
                raise ValueError('Bin labels must be one fewer than '
                                 'the number of bin edges')
            levels = labels

        levels = np.asarray(levels, dtype=object)
        np.putmask(ids, na_mask, 0)
        fac = Categorical(ids - 1, levels, ordered=True, fastpath=True)
    else:
        fac = ids - 1
        if has_nas:
            fac = fac.astype(np.float64)
            np.putmask(fac, na_mask, np.nan)

    return fac, bins