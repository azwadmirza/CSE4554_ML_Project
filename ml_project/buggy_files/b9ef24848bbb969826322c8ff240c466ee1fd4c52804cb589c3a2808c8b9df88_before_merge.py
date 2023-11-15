def period_range(start=None, end=None, periods=None, freq='D'):
    """
    Return a fixed frequency datetime index, with day (calendar) as the default
    frequency


    Parameters
    ----------
    start :
    end :
    normalize : bool, default False
        Normalize start/end dates to midnight before generating date range

    Returns
    -------

    """
    return PeriodIndex(start=start, end=end, periods=periods,
                       freq=freq)