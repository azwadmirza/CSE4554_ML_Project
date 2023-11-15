def rolling_count(arg, window, freq=None, time_rule=None):
    """
    Rolling count of number of non-NaN observations inside provided window.

    Parameters
    ----------
    arg :  DataFrame or numpy ndarray-like
    window : Number of observations used for calculating statistic
    freq : None or string alias / date offset object, default=None
        Frequency to conform to before computing statistic

    Returns
    -------
    rolling_count : type of caller
    """
    arg = _conv_timerule(arg, freq, time_rule)
    window = min(window, len(arg))

    return_hook, values = _process_data_structure(arg, kill_inf=False)

    converted = np.isfinite(values).astype(float)
    result = rolling_sum(converted, window, min_periods=1,
                         time_rule=time_rule)

    # putmask here?
    result[np.isnan(result)] = 0

    return return_hook(result)