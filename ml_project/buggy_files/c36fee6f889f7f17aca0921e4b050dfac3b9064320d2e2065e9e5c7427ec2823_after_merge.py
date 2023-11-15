def _topomap_animation(evoked, ch_type='mag', times=None, frame_rate=None,
                       butterfly=False, blit=True, show=True):
    """Make animation of evoked data as topomap timeseries. Animation can be
    paused/resumed with left mouse button. Left and right arrow keys can be
    used to move backward or forward in time.

    Parameters
    ----------
    evoked : instance of Evoked
        The evoked data.
    ch_type : str | None
        Channel type to plot. Accepted data types: 'mag', 'grad', 'eeg'.
        If None, first available channel type from ('mag', 'grad', 'eeg') is
        used. Defaults to None.
    times : array of floats | None
        The time points to plot. If None, 10 evenly spaced samples are
        calculated over the evoked time series. Defaults to None.
    frame_rate : int | None
        Frame rate for the animation in Hz. If None, frame rate = sfreq / 10.
        Defaults to None.
    butterfly : bool
        Whether to plot the data as butterfly plot under the topomap.
        Defaults to False.
    blit : bool
        Whether to use blit to optimize drawing. In general, it is recommended
        to use blit in combination with ``show=True``. If you intend to save
        the animation it is better to disable blit. For MacOSX blit is always
        disabled. Defaults to True.
    show : bool
        Whether to show the animation. Defaults to True.

    Returns
    -------
    fig : instance of matplotlib figure
        The figure.
    anim : instance of matplotlib FuncAnimation
        Animation of the topomap.

    Notes
    -----
    .. versionadded:: 0.12.0
    """
    from matplotlib import pyplot as plt, animation
    if ch_type is None:
        ch_type = _picks_by_type(evoked.info)[0][0]
    if ch_type not in ('mag', 'grad', 'eeg'):
        raise ValueError("Channel type not supported. Supported channel "
                         "types include 'mag', 'grad' and 'eeg'.")
    if times is None:
        times = np.linspace(evoked.times[0], evoked.times[-1], 10)
    times = np.array(times)

    if times.ndim != 1:
        raise ValueError('times must be 1D, got %d dimensions' % times.ndim)
    if max(times) > evoked.times[-1] or min(times) < evoked.times[0]:
        raise ValueError('All times must be inside the evoked time series.')
    frames = [np.abs(evoked.times - time).argmin() for time in times]

    blit = False if plt.get_backend() == 'MacOSX' else blit
    picks, pos, merge_grads, _, ch_type = _prepare_topo_plot(evoked,
                                                             ch_type=ch_type,
                                                             layout=None)
    data = evoked.data[picks, :]
    data *= _handle_default('scalings')[ch_type]

    fig = plt.figure()
    offset = 0. if blit else 0.4  # XXX: blit changes the sizes for some reason
    ax = plt.axes([0. + offset / 2., 0. + offset / 2., 1. - offset,
                   1. - offset], xlim=(-1, 1), ylim=(-1, 1))
    if butterfly:
        ax_line = plt.axes([0.2, 0.05, 0.6, 0.1], xlim=(evoked.times[0],
                                                        evoked.times[-1]))
    else:
        ax_line = None
    if isinstance(frames, int):
        frames = np.linspace(0, len(evoked.times) - 1, frames).astype(int)
    ax_cbar = plt.axes([0.85, 0.1, 0.05, 0.8])
    ax_cbar.set_title(_handle_default('units')[ch_type], fontsize=10)

    params = {'data': data, 'pos': pos, 'all_times': evoked.times, 'frame': 0,
              'frames': frames, 'butterfly': butterfly, 'blit': blit,
              'pause': False, 'times': times}
    init_func = partial(_init_anim, ax=ax, ax_cbar=ax_cbar, ax_line=ax_line,
                        params=params, merge_grads=merge_grads)
    animate_func = partial(_animate, ax=ax, ax_line=ax_line, params=params)
    pause_func = partial(_pause_anim, params=params)
    fig.canvas.mpl_connect('button_press_event', pause_func)
    key_press_func = partial(_key_press, params=params)
    fig.canvas.mpl_connect('key_press_event', key_press_func)
    if frame_rate is None:
        frame_rate = evoked.info['sfreq'] / 10.
    interval = 1000 / frame_rate  # interval is in ms
    anim = animation.FuncAnimation(fig, animate_func, init_func=init_func,
                                   frames=len(frames), interval=interval,
                                   blit=blit)
    fig.mne_animation = anim  # to make sure anim is not garbage collected
    plt_show(show, block=False)
    if 'line' in params:
        # Finally remove the vertical line so it does not appear in saved fig.
        params['line'].remove()

    return fig, anim