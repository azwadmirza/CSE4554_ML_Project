def _set_psd_plot_params(info, proj, picks, ax, area_mode):
    """Set PSD plot params."""
    import matplotlib.pyplot as plt
    if area_mode not in [None, 'std', 'range']:
        raise ValueError('"area_mode" must be "std", "range", or None')

    # XXX this could be refactored more with e.g., plot_evoked
    megs = ['mag', 'grad', False, False, False]
    eegs = [False, False, True, False, False]
    seegs = [False, False, False, True, False]
    ecogs = [False, False, False, False, True]
    names = ['mag', 'grad', 'eeg', 'seeg', 'ecog']
    titles = _handle_default('titles', None)
    units = _handle_default('units', None)
    scalings = _handle_default('scalings', None)
    picks_list = list()
    titles_list = list()
    units_list = list()
    scalings_list = list()
    for meg, eeg, seeg, ecog, name in zip(megs, eegs, seegs, ecogs, names):
        these_picks = pick_types(info, meg=meg, eeg=eeg, seeg=seeg, ecog=ecog,
                                 ref_meg=False)
        if picks is not None:
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

    make_label = False
    fig = None
    if ax is None:
        fig = plt.figure()
        ax_list = list()
        for ii in range(len(picks_list)):
            # Make x-axes change together
            if ii > 0:
                ax_list.append(plt.subplot(len(picks_list), 1, ii + 1,
                                           sharex=ax_list[0]))
            else:
                ax_list.append(plt.subplot(len(picks_list), 1, ii + 1))
        make_label = True
    else:
        fig = ax_list[0].get_figure()

    return (fig, picks_list, titles_list, units_list, scalings_list,
            ax_list, make_label)