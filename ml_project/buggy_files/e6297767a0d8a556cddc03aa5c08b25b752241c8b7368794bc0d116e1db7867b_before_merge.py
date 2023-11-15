def rolling_window(arg, window=None, win_type=None, min_periods=None,
                   freq=None, center=False, mean=True,
                   axis=0, **kwargs):
    """
    Applies a moving window of type ``window_type`` and size ``window``
    on the data.

    Parameters
    ----------
    arg : Series, DataFrame
    window : int or ndarray
        Weighting window specification. If the window is an integer, then it is
        treated as the window length and win_type is required
    win_type : str, default None
        Window type (see Notes)
    min_periods : int, default None
        Minimum number of observations in window required to have a value
        (otherwise result is NA).
    freq : string or DateOffset object, optional (default None)
        Frequency to conform the data to before computing the statistic. Specified
        as a frequency string or DateOffset object.
    center : boolean, default False
        Whether the label should correspond with center of window
    mean : boolean, default True
        If True computes weighted mean, else weighted sum
    axis : {0, 1}, default 0

    Returns
    -------
    y : type of input argument

    Notes
    -----
    The recognized window types are:

    * ``boxcar``
    * ``triang``
    * ``blackman``
    * ``hamming``
    * ``bartlett``
    * ``parzen``
    * ``bohman``
    * ``blackmanharris``
    * ``nuttall``
    * ``barthann``
    * ``kaiser`` (needs beta)
    * ``gaussian`` (needs std)
    * ``general_gaussian`` (needs power, width)
    * ``slepian`` (needs width).
    
    By default, the result is set to the right edge of the window. This can be
    changed to the center of the window by setting ``center=True``.

    The `freq` keyword is used to conform time series data to a specified
    frequency by resampling the data. This is done with the default parameters
    of :meth:`~pandas.Series.resample` (i.e. using the `mean`).
    """
    if isinstance(window, (list, tuple, np.ndarray)):
        if win_type is not None:
            raise ValueError(('Do not specify window type if using custom '
                              'weights'))
        window = pdcom._asarray_tuplesafe(window).astype(float)
    elif pdcom.is_integer(window):  # window size
        if win_type is None:
            raise ValueError('Must specify window type')
        try:
            import scipy.signal as sig
        except ImportError:
            raise ImportError('Please install scipy to generate window weight')
        win_type = _validate_win_type(win_type, kwargs)  # may pop from kwargs
        window = sig.get_window(win_type, window).astype(float)
    else:
        raise ValueError('Invalid window %s' % str(window))

    minp = _use_window(min_periods, len(window))

    arg = _conv_timerule(arg, freq)
    return_hook, values = _process_data_structure(arg)

    f = lambda x: algos.roll_window(x, window, minp, avg=mean)
    result = np.apply_along_axis(f, axis, values)

    rs = return_hook(result)
    if center:
        rs = _center_window(rs, len(window), axis)
    return rs