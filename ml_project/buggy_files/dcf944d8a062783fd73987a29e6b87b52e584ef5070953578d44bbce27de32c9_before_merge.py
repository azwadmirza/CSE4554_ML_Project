def plot_epochs_image(epochs, picks=None, sigma=0., vmin=None,
                      vmax=None, colorbar=True, order=None, show=True,
                      units=None, scalings=None, cmap='RdBu_r',
                      fig=None, axes=None, overlay_times=None):
    """Plot Event Related Potential / Fields image

    Parameters
    ----------
    epochs : instance of Epochs
        The epochs.
    picks : int | array-like of int | None
        The indices of the channels to consider. If None, the first
        five good channels are plotted.
    sigma : float
        The standard deviation of the Gaussian smoothing to apply along
        the epoch axis to apply in the image. If 0., no smoothing is applied.
    vmin : float
        The min value in the image. The unit is uV for EEG channels,
        fT for magnetometers and fT/cm for gradiometers.
    vmax : float
        The max value in the image. The unit is uV for EEG channels,
        fT for magnetometers and fT/cm for gradiometers.
    colorbar : bool
        Display or not a colorbar.
    order : None | array of int | callable
        If not None, order is used to reorder the epochs on the y-axis
        of the image. If it's an array of int it should be of length
        the number of good epochs. If it's a callable the arguments
        passed are the times vector and the data as 2d array
        (data.shape[1] == len(times).
    show : bool
        Show figure if True.
    units : dict | None
        The units of the channel types used for axes lables. If None,
        defaults to `units=dict(eeg='uV', grad='fT/cm', mag='fT')`.
    scalings : dict | None
        The scalings of the channel types to be applied for plotting.
        If None, defaults to `scalings=dict(eeg=1e6, grad=1e13, mag=1e15,
        eog=1e6)`.
    cmap : matplotlib colormap
        Colormap.
    fig : matplotlib figure | None
        Figure instance to draw the image to. Figure must contain two axes for
        drawing the single trials and evoked responses. If None a new figure is
        created. Defaults to None.
    axes : list of matplotlib axes | None
        List of axes instances to draw the image, erp and colorbar to.
        Must be of length three if colorbar is True (with the last list element
        being the colorbar axes) or two if colorbar is False. If both fig and
        axes are passed an error is raised. Defaults to None.
    overlay_times : array-like, shape (n_epochs,) | None
        If not None the parameter is interpreted as time instants in seconds
        and is added to the image. It is typically useful to display reaction
        times. Note that it is defined with respect to the order
        of epochs such that overlay_times[0] corresponds to epochs[0].

    Returns
    -------
    figs : lists of matplotlib figures
        One figure per channel displayed.
    """
    from scipy import ndimage
    units = _handle_default('units', units)
    scalings = _handle_default('scalings', scalings)

    import matplotlib.pyplot as plt
    if picks is None:
        picks = pick_types(epochs.info, meg=True, eeg=True, ref_meg=False,
                           exclude='bads')[:5]

    if set(units.keys()) != set(scalings.keys()):
        raise ValueError('Scalings and units must have the same keys.')

    picks = np.atleast_1d(picks)
    if (fig is not None or axes is not None) and len(picks) > 1:
        raise ValueError('Only single pick can be drawn to a figure.')
    if axes is not None:
        if fig is not None:
            raise ValueError('Both figure and axes were passed, please'
                             'decide between the two.')
        from .utils import _validate_if_list_of_axes
        oblig_len = 3 if colorbar else 2
        _validate_if_list_of_axes(axes, obligatory_len=oblig_len)
        ax1, ax2 = axes[:2]
        # if axes were passed - we ignore fig param and get figure from axes
        fig = ax1.get_figure()
        if colorbar:
            ax3 = axes[-1]
    evoked = epochs.average(picks)
    data = epochs.get_data()[:, picks, :]
    scale_vmin = True if vmin is None else False
    scale_vmax = True if vmax is None else False
    vmin, vmax = _setup_vmin_vmax(data, vmin, vmax)

    if overlay_times is not None and len(overlay_times) != len(data):
        raise ValueError('size of overlay_times parameter (%s) do not '
                         'match the number of epochs (%s).'
                         % (len(overlay_times), len(data)))

    if overlay_times is not None:
        overlay_times = np.array(overlay_times)
        times_min = np.min(overlay_times)
        times_max = np.max(overlay_times)
        if ((times_min < epochs.tmin) or (times_max > epochs.tmax)):
            warn('Some values in overlay_times fall outside of the epochs '
                 'time interval (between %s s and %s s)'
                 % (epochs.tmin, epochs.tmax))

    figs = list()
    for i, (this_data, idx) in enumerate(zip(np.swapaxes(data, 0, 1), picks)):
        if fig is None:
            this_fig = plt.figure()
        else:
            this_fig = fig
        figs.append(this_fig)

        ch_type = channel_type(epochs.info, idx)
        if ch_type not in scalings:
            # We know it's not in either scalings or units since keys match
            raise KeyError('%s type not in scalings and units' % ch_type)
        this_data *= scalings[ch_type]

        this_order = order
        if callable(order):
            this_order = order(epochs.times, this_data)

        if this_order is not None and (len(this_order) != len(this_data)):
            raise ValueError('size of order parameter (%s) does not '
                             'match the number of epochs (%s).'
                             % (len(this_order), len(this_data)))

        this_overlay_times = None
        if overlay_times is not None:
            this_overlay_times = overlay_times

        if this_order is not None:
            this_order = np.asarray(this_order)
            this_data = this_data[this_order]
            if this_overlay_times is not None:
                this_overlay_times = this_overlay_times[this_order]

        if sigma > 0.:
            this_data = ndimage.gaussian_filter1d(this_data, sigma=sigma,
                                                  axis=0)
        plt.figure(this_fig.number)
        if axes is None:
            ax1 = plt.subplot2grid((3, 10), (0, 0), colspan=9, rowspan=2)
            ax2 = plt.subplot2grid((3, 10), (2, 0), colspan=9, rowspan=1)
            if colorbar:
                ax3 = plt.subplot2grid((3, 10), (0, 9), colspan=1, rowspan=3)
        if scale_vmin:
            vmin *= scalings[ch_type]
        if scale_vmax:
            vmax *= scalings[ch_type]
        im = ax1.imshow(this_data,
                        extent=[1e3 * epochs.times[0], 1e3 * epochs.times[-1],
                                0, len(data)],
                        aspect='auto', origin='lower', interpolation='nearest',
                        vmin=vmin, vmax=vmax, cmap=cmap)
        if this_overlay_times is not None:
            plt.plot(1e3 * this_overlay_times, 0.5 + np.arange(len(this_data)),
                     'k', linewidth=2)
        ax1.set_title(epochs.ch_names[idx])
        ax1.set_ylabel('Epochs')
        ax1.axis('auto')
        ax1.axis('tight')
        ax1.axvline(0, color='m', linewidth=3, linestyle='--')
        evoked_data = scalings[ch_type] * evoked.data[i]
        ax2.plot(1e3 * evoked.times, evoked_data)
        ax2.set_xlabel('Time (ms)')
        ax2.set_xlim([1e3 * evoked.times[0], 1e3 * evoked.times[-1]])
        ax2.set_ylabel(units[ch_type])
        evoked_vmin = min(evoked_data) * 1.1 if scale_vmin else vmin
        evoked_vmax = max(evoked_data) * 1.1 if scale_vmax else vmax
        if scale_vmin or scale_vmax:
            evoked_vmax = max(np.abs([evoked_vmax, evoked_vmin]))
            evoked_vmin = -evoked_vmax
        ax2.set_ylim([evoked_vmin, evoked_vmax])
        ax2.axvline(0, color='m', linewidth=3, linestyle='--')
        if colorbar:
            plt.colorbar(im, cax=ax3)
            tight_layout(fig=this_fig)

    plt_show(show)
    return figs