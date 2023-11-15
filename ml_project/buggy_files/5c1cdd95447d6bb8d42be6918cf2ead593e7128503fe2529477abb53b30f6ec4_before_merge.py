def _rolling_moment(arg, window, func, minp, axis=0, freq=None, center=False,
                    args=(), kwargs={}, **kwds):
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
    freq : None or string alias / date offset object, default=None
        Frequency to conform to before computing statistic
    center : boolean, default False
        Whether the label should correspond with center of window
    args : tuple
        Passed on to func
    kwargs : dict
        Passed on to func

    Returns
    -------
    y : type of input
    """
    arg = _conv_timerule(arg, freq)
    calc = lambda x: func(x, window, minp=minp, args=args, kwargs=kwargs,
                          **kwds)
    return_hook, values = _process_data_structure(arg)
    # actually calculate the moment. Faster way to do this?
    if values.ndim > 1:
        result = np.apply_along_axis(calc, axis, values)
    else:
        result = calc(values)

    rs = return_hook(result)
    if center:
        rs = _center_window(rs, window, axis)
    return rs