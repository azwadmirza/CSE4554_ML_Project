def rolling_quantile(arg, window, quantile, min_periods=None, time_rule=None):
    """Moving quantile

    Parameters
    ----------
    arg : Series, DataFrame
    window : Number of observations used for calculating statistic
    quantile : 0 <= quantile <= 1
    min_periods : int
        Minimum number of observations in window required to have a value
    time_rule : {None, 'WEEKDAY', 'EOM', 'W@MON', ...}, default=None
        Name of time rule to conform to before computing statistic

    Returns
    -------
    y : type of input argument
    """

    def call_cython(arg, window, minp):
        minp = _use_window(minp, window)
        return _tseries.roll_quantile(arg, window, minp, quantile)
    return _rolling_moment(arg, window, call_cython, min_periods,
                           time_rule=time_rule)