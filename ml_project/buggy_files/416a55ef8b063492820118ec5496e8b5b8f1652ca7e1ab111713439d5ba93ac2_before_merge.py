def _nanpercentile1d(arr1d, q, overwrite_input=False, interpolation='linear'):
    """
    Private function for rank 1 arrays. Compute percentile ignoring NaNs.
    See nanpercentile for parameter usage

    """
    c = np.isnan(arr1d)
    s = np.where(c)[0]
    if s.size == arr1d.size:
        warnings.warn("All-NaN slice encountered", RuntimeWarning)
        return np.nan
    elif s.size == 0:
        return np.percentile(arr1d, q, overwrite_input=overwrite_input,
                             interpolation=interpolation)
    else:
        if overwrite_input:
            x = arr1d
        else:
            x = arr1d.copy()
        # select non-nans at end of array
        enonan = arr1d[-s.size:][~c[-s.size:]]
        # fill nans in beginning of array with non-nans of end
        x[s[:enonan.size]] = enonan
        # slice nans away
        return np.percentile(x[:-s.size], q, overwrite_input=True,
                             interpolation=interpolation)