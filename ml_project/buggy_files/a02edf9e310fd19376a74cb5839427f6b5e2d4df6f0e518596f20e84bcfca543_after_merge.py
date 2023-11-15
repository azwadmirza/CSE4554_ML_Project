def rolling_count(arg, window, freq=None, center=False, how=None):
    """
    Rolling count of number of non-NaN observations inside provided window.

    Parameters
    ----------
    arg :  DataFrame or numpy ndarray-like
    window : int
        Size of the moving window. This is the number of observations used for
        calculating the statistic.
    freq : string or DateOffset object, optional (default None)
        Frequency to conform the data to before computing the statistic. Specified
        as a frequency string or DateOffset object.
    center : boolean, default False
        Whether the label should correspond with center of window
    how : string, default 'mean'
        Method for down- or re-sampling

    Returns
    -------
    rolling_count : type of caller

    Notes
    -----
    The `freq` keyword is used to conform time series data to a specified
    frequency by resampling the data. This is done with the default parameters
    of :meth:`~pandas.Series.resample` (i.e. using the `mean`).
    """
    arg = _conv_timerule(arg, freq, how)
    window = min(window, len(arg))

    return_hook, values = _process_data_structure(arg, kill_inf=False)

    converted = np.isfinite(values).astype(float)
    result = rolling_sum(converted, window, min_periods=1,
                         center=center)  # already converted

    # putmask here?
    result[np.isnan(result)] = 0

    return return_hook(result)