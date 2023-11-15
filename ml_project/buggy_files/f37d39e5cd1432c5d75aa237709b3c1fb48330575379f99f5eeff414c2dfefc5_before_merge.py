def _plot_corrmap(data, subjs, indices, ch_type, ica, label, show, outlines,
                  layout, cmap, contours, template=True):
    """Customized ica.plot_components for corrmap"""
    if not template:
        title = 'Detected components'
        if label is not None:
            title += ' of type ' + label
    else:
        title = "Supplied template"

    picks = list(range(len(data)))

    p = 20
    if len(picks) > p:  # plot components by sets of 20
        n_components = len(picks)
        figs = [_plot_corrmap(data[k:k + p], subjs[k:k + p],
                indices[k:k + p], ch_type, ica, label, show,
                outlines=outlines, layout=layout, cmap=cmap,
                contours=contours)
                for k in range(0, n_components, p)]
        return figs
    elif np.isscalar(picks):
        picks = [picks]

    data_picks, pos, merge_grads, names, _ = _prepare_topo_plot(
        ica, ch_type, layout)
    pos, outlines = _check_outlines(pos, outlines)

    data = np.atleast_2d(data)
    data = data[:, data_picks]

    # prepare data for iteration
    fig, axes = _prepare_trellis(len(picks), max_col=5)
    fig.suptitle(title)

    if merge_grads:
        from ..channels.layout import _merge_grad_data
    for ii, data_, ax, subject, idx in zip(picks, data, axes, subjs, indices):
        if template:
            ttl = 'Subj. {0}, IC {1}'.format(subject, idx)
            ax.set_title(ttl, fontsize=12)
        data_ = _merge_grad_data(data_) if merge_grads else data_
        vmin_, vmax_ = _setup_vmin_vmax(data_, None, None)
        plot_topomap(data_.flatten(), pos, vmin=vmin_, vmax=vmax_,
                     res=64, axis=ax, cmap=cmap, outlines=outlines,
                     image_mask=None, contours=contours, show=False,
                     image_interp='bilinear')[0]
        ax.set_yticks([])
        ax.set_xticks([])
        ax.set_frame_on(False)
    tight_layout(fig=fig)
    fig.subplots_adjust(top=0.8)
    fig.canvas.draw()
    plt_show(show)
    return fig