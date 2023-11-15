def tsplot(series, plotf, **kwargs):
    """
    Plots a Series on the given Matplotlib axes or the current axes

    Parameters
    ----------
    axes : Axes
    series : Series

    Notes
    _____
    Supports same kwargs as Axes.plot

    """
    # Used inferred freq is possible, need a test case for inferred
    if 'ax' in kwargs:
        ax = kwargs.pop('ax')
    else:
        import matplotlib.pyplot as plt
        ax = plt.gca()

    freq = _get_freq(ax, series)
    # resample against axes freq if necessary
    if freq is None: # pragma: no cover
        raise ValueError('Cannot use dynamic axis without frequency info')
    else:
        ax_freq = getattr(ax, 'freq', None)
        if (ax_freq is not None) and (freq != ax_freq):
            if frequencies.is_subperiod(freq, ax_freq): # downsample
                how = kwargs.pop('how', 'last')
                series = series.resample(ax_freq, how=how)
            elif frequencies.is_superperiod(freq, ax_freq):
                series = series.resample(ax_freq)
            else: # one freq is weekly
                how = kwargs.pop('how', 'last')
                series = series.resample('D', how=how, fill_method='pad')
                series = series.resample(ax_freq, how=how, fill_method='pad')
            freq = ax_freq

    # Convert DatetimeIndex to PeriodIndex
    if isinstance(series.index, DatetimeIndex):
        series = series.to_period(freq=freq)

    style = kwargs.pop('style', None)

    # Specialized ts plotting attributes for Axes
    ax.freq = freq
    xaxis = ax.get_xaxis()
    xaxis.freq = freq
    ax.legendlabels = [kwargs.get('label', None)]
    ax.view_interval = None
    ax.date_axis_info = None

    # format args and lot
    args = _maybe_mask(series)

    if style is not None:
        args.append(style)

    plotf(ax, *args,  **kwargs)

    format_dateaxis(ax, ax.freq)

    left, right = _get_xlim(ax.get_lines())
    ax.set_xlim(left, right)

    return ax