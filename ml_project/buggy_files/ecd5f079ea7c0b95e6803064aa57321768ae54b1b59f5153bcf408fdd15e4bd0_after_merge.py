def _set_psd_plot_params(info, proj, picks, ax, area_mode):
    """Set PSD plot params."""
    import matplotlib.pyplot as plt
    _check_option('area_mode', area_mode, [None, 'std', 'range'])
    picks = _picks_to_idx(info, picks)

    # XXX this could be refactored more with e.g., plot_evoked
    # XXX when it's refactored, Report._render_raw will need to be updated
    titles = _handle_default('titles', None)
    units = _handle_default('units', None)
    scalings = _handle_default('scalings', None)
    picks_list = list()
    titles_list = list()
    units_list = list()
    scalings_list = list()
    for name in _DATA_CH_TYPES_SPLIT:
        kwargs = dict(meg=False, ref_meg=False, exclude=[])
        if name in ('mag', 'grad'):
            kwargs['meg'] = name
        elif name in ('fnirs_raw', 'fnirs_od', 'hbo', 'hbr'):
            kwargs['fnirs'] = name
        else:
            kwargs[name] = True
        these_picks = pick_types(info, **kwargs)
        these_picks = np.intersect1d(these_picks, picks)
        if len(these_picks) > 0:
            picks_list.append(these_picks)
            titles_list.append(titles[name])
            units_list.append(units[name])
            scalings_list.append(scalings[name])
    if len(picks_list) == 0:
        raise RuntimeError('No data channels found')
    if ax is not None:
        if isinstance(ax, plt.Axes):
            ax = [ax]
        if len(ax) != len(picks_list):
            raise ValueError('For this dataset with picks=None %s axes '
                             'must be supplied, got %s'
                             % (len(picks_list), len(ax)))
        ax_list = ax
    del picks

    fig = None
    if ax is None:
        fig, ax_list = plt.subplots(len(picks_list), 1, sharex=True,
                                    squeeze=False)
        ax_list = list(ax_list[:, 0])
        make_label = True
    else:
        fig = ax_list[0].get_figure()
        make_label = len(ax_list) == len(fig.axes)

    return (fig, picks_list, titles_list, units_list, scalings_list,
            ax_list, make_label)