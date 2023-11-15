def prep_ticks(ax, index, ax_type, props):
    """Prepare axis obj belonging to axes obj.

    positional arguments:
    ax - the mpl axes instance
    index - the index of the axis in `props`
    ax_type - 'x' or 'y' (for now)
    props - an mplexporter poperties dictionary

    """
    axis_dict = dict()
    if ax_type == 'x':
        axis = ax.get_xaxis()
    elif ax_type == 'y':
        axis = ax.get_yaxis()
    else:
        return dict() # whoops!

    scale = props['axes'][index]['scale']
    if scale == 'linear':
        # get tick location information
        try:
            tickvalues = props['axes'][index]['tickvalues']
            tick0 = tickvalues[0]
            dticks = [round(tickvalues[i]-tickvalues[i-1], 12)
                      for i in range(1, len(tickvalues) - 1)]
            if all([dticks[i] == dticks[i-1]
                    for i in range(1, len(dticks) - 1)]):
                dtick = tickvalues[1] - tickvalues[0]
            else:
                warnings.warn("'linear' {0}-axis tick spacing not even, "
                              "ignoring mpl tick formatting.".format(ax_type))
                raise TypeError
        except (IndexError, TypeError):
            axis_dict['nticks'] = props['axes'][index]['nticks']
        else:
            axis_dict['tick0'] = tick0
            axis_dict['dtick'] = dtick
            axis_dict['tickmode'] = False
    elif scale == 'log':
        try:
            axis_dict['tick0'] = props['axes'][index]['tickvalues'][0]
            axis_dict['dtick'] = props['axes'][index]['tickvalues'][1] - \
                            props['axes'][index]['tickvalues'][0]
            axis_dict['tickmode'] = False
        except (IndexError, TypeError):
            axis_dict = dict(nticks=props['axes'][index]['nticks'])
        base = axis.get_transform().base
        if base == 10:
            if ax_type == 'x':
                axis_dict['range'] = [math.log10(props['xlim'][0]),
                                 math.log10(props['xlim'][1])]
            elif ax_type == 'y':
                axis_dict['range'] = [math.log10(props['ylim'][0]),
                                 math.log10(props['ylim'][1])]
        else:
            axis_dict = dict(range=None, type='linear')
            warnings.warn("Converted non-base10 {0}-axis log scale to 'linear'"
                          "".format(ax_type))
    else:
        return dict()
    # get tick label formatting information
    formatter = axis.get_major_formatter().__class__.__name__
    if ax_type == 'x' and 'DateFormatter' in formatter:
        axis_dict['type'] = 'date'
        try:
            axis_dict['tick0'] = mpl_dates_to_datestrings(
                axis_dict['tick0'], formatter
            )
        except KeyError:
            pass
        finally:
            axis_dict.pop('dtick', None)
            axis_dict.pop('tickmode', None)
            axis_dict['range'] = mpl_dates_to_datestrings(
                props['xlim'], formatter
            )

    if formatter == 'LogFormatterMathtext':
        axis_dict['exponentformat'] = 'e'
    return axis_dict