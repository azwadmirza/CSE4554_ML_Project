def rolling_apply(arg, window, func, min_periods=None, time_rule=None):
    """Generic moving function application

    Parameters
    ----------
    arg : Series, DataFrame
    window : Number of observations used for calculating statistic
    func : function
        Must produce a single value from an ndarray input
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
        return _tseries.roll_generic(arg, window, minp, func)
    return _rolling_moment(arg, window, call_cython, min_periods,
                           time_rule=time_rule)