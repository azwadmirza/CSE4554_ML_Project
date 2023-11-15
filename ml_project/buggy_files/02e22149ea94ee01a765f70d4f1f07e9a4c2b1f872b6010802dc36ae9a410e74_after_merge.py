def rolling_quantile(arg, window, quantile, min_periods=None, freq=None,
                     time_rule=None):
    """Moving quantile

    Parameters
    ----------
    arg : Series, DataFrame
    window : Number of observations used for calculating statistic
    quantile : 0 <= quantile <= 1
    min_periods : int
        Minimum number of observations in window required to have a value
    freq : None or string alias / date offset object, default=None
        Frequency to conform to before computing statistic

    Returns
    -------
    y : type of input argument
    """

    def call_cython(arg, window, minp):
        minp = _use_window(minp, window)
        return lib.roll_quantile(arg, window, minp, quantile)
    return _rolling_moment(arg, window, call_cython, min_periods,
                           freq=freq, time_rule=time_rule)