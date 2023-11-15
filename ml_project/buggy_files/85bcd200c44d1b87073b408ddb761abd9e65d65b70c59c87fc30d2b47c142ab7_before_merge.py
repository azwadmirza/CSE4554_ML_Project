def tsplot(series, plotf, *args, **kwargs):
    """
    Plots a Series on the given Matplotlib axes object

    Parameters
    ----------
    axes : Axes
    series : Series

    Notes
    _____
    Supports same args and kwargs as Axes.plot

    """
    # Used inferred freq is possible, need a test case for inferred
    freq = getattr(series.index, 'freq', None)
    if freq is None and hasattr(series.index, 'inferred_freq'):
        freq = series.index.inferred_freq

    if isinstance(freq, DateOffset):
        freq = freq.rule_code

    freq = frequencies.to_calendar_freq(freq)
    # Convert DatetimeIndex to PeriodIndex
    if isinstance(series.index, DatetimeIndex):
        idx = series.index.to_period(freq=freq)
        series = Series(series.values, idx, name=series.name)

    if not isinstance(series.index, PeriodIndex):
        #try to get it to DatetimeIndex then to period
        if series.index.inferred_type == 'datetime':
            idx = DatetimeIndex(series.index).to_period(freq=freq)
            series = Series(series.values, idx, name=series.name)
        else:
            raise TypeError('series argument to tsplot must have '
                            'DatetimeIndex or PeriodIndex')

    if freq != series.index.freq:
        series = series.asfreq(freq)

    series = series.dropna()

    if 'ax' in kwargs:
        ax = kwargs.pop('ax')
    else:
        ax = plt.gca()

    # Specialized ts plotting attributes for Axes
    ax.freq = freq
    xaxis = ax.get_xaxis()
    xaxis.freq = freq
    xaxis.converter = DateConverter
    ax.legendlabels = [kwargs.get('label', None)]
    ax.view_interval = None
    ax.date_axis_info = None

    # format args and lot
    args = _check_plot_params(series, series.index, freq, *args)
    plotted = plotf(ax, *args,  **kwargs)

    format_dateaxis(ax, ax.freq)

    # when adding a right axis (using add_yaxis), for some reason the
    # x axis limits don't get properly set. This gets around the problem
    xlim = ax.get_xlim()
    if xlim[0] == 0.0 and xlim[1] == 1.0:
        # if xlim still at default values, autoscale the axis
        ax.autoscale_view()

    left = series.index[0] #get_datevalue(series.index[0], freq)
    right = series.index[-1] #get_datevalue(series.index[-1], freq)
    ax.set_xlim(left, right)

    return plotted