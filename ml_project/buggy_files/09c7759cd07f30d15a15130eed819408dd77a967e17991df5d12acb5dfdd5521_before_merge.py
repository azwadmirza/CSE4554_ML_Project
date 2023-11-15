def _butterfly_onselect(xmin, xmax, ch_types, evoked, text=None):
    """Function for drawing topomaps from the selected area."""
    import matplotlib.pyplot as plt
    ch_types = [type for type in ch_types if type in ('eeg', 'grad', 'mag')]
    vert_lines = list()
    if text is not None:
        text.set_visible(True)
        ax = text.axes
        ylim = ax.get_ylim()
        vert_lines.append(ax.plot([xmin, xmin], ylim, zorder=0, color='red'))
        vert_lines.append(ax.plot([xmax, xmax], ylim, zorder=0, color='red'))
        fill = ax.fill_betweenx(ylim, x1=xmin, x2=xmax, alpha=0.2,
                                color='green')
        evoked_fig = plt.gcf()
        evoked_fig.canvas.draw()
        evoked_fig.canvas.flush_events()
    times = evoked.times
    xmin *= 0.001
    minidx = np.abs(times - xmin).argmin()
    xmax *= 0.001
    maxidx = np.abs(times - xmax).argmin()
    fig, axarr = plt.subplots(1, len(ch_types), squeeze=False,
                              figsize=(3 * len(ch_types), 3))
    for idx, ch_type in enumerate(ch_types):
        picks, pos, merge_grads, _, ch_type = _prepare_topo_plot(evoked,
                                                                 ch_type,
                                                                 layout=None)
        data = evoked.data[picks, minidx:maxidx]
        if merge_grads:
            from ..channels.layout import _merge_grad_data
            data = _merge_grad_data(data)
            title = '%s RMS' % ch_type
        else:
            title = ch_type
        data = np.average(data, axis=1)
        axarr[0][idx].set_title(title)
        plot_topomap(data, pos, axes=axarr[0][idx], show=False)

    fig.suptitle('Average over %.2fs - %.2fs' % (xmin, xmax), fontsize=15,
                 y=0.1)
    tight_layout(pad=2.0, fig=fig)
    plt_show()
    if text is not None:
        text.set_visible(False)
        close_callback = partial(_topo_closed, ax=ax, lines=vert_lines,
                                 fill=fill)
        fig.canvas.mpl_connect('close_event', close_callback)
        evoked_fig.canvas.draw()
        evoked_fig.canvas.flush_events()