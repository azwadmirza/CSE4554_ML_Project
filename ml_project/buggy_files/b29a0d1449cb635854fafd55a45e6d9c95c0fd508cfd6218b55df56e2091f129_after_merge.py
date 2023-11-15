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
        # Convert DatetimeIndex to PeriodIndex
        if isinstance(series.index, DatetimeIndex):
            series = series.to_period(freq=freq)
        freq, ax_freq, series = _maybe_resample(series, ax, freq, plotf,
                                                kwargs)

    # Set ax with freq info
    _decorate_axes(ax, freq, kwargs)

    # mask missing values
    args = _maybe_mask(series)

    # how to make sure ax.clear() flows through?
    if not hasattr(ax, '_plot_data'):
        ax._plot_data = []
    ax._plot_data.append((series, kwargs))

    # styles
    style = kwargs.pop('style', None)
    if style is not None:
        args.append(style)

    lines = plotf(ax, *args,  **kwargs)
    label = kwargs.get('label', None)

    # set date formatter, locators and rescale limits
    format_dateaxis(ax, ax.freq)
    left, right = _get_xlim(ax.get_lines())
    ax.set_xlim(left, right)

    return lines