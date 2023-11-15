def _rolling_moment(arg, window, func, minp, axis=0, time_rule=None):
    """
    Rolling statistical measure using supplied function. Designed to be
    used with passed-in Cython array-based functions.

    Parameters
    ----------
    arg :  DataFrame or numpy ndarray-like
    window : Number of observations used for calculating statistic
    func : Cython function to compute rolling statistic on raw series
    minp : int
        Minimum number of observations required to have a value
    axis : int, default 0
    time_rule : string or DateOffset
        Time rule to conform to before computing result

    Returns
    -------
    y : type of input
    """
    arg = _conv_timerule(arg, time_rule)
    calc = lambda x: func(x, window, minp=minp)
    return_hook, values = _process_data_structure(arg)
    # actually calculate the moment. Faster way to do this?
    result = np.apply_along_axis(calc, axis, values)

    return return_hook(result)