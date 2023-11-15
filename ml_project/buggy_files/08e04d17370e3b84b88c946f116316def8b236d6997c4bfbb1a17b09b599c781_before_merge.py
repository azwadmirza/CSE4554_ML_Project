def _label_clicked(pos, params):
    """Function for plotting independent components on click to label."""
    import matplotlib.pyplot as plt
    offsets = np.array(params['offsets']) + params['offsets'][0]
    line_idx = np.searchsorted(offsets, pos[1]) + params['ch_start']
    if line_idx >= len(params['picks']):
        return
    ic_idx = [params['picks'][line_idx]]
    types = list()
    info = params['ica'].info
    if len(pick_types(info, meg=False, eeg=True, ref_meg=False)) > 0:
        types.append('eeg')
    if len(pick_types(info, meg='mag', ref_meg=False)) > 0:
        types.append('mag')
    if len(pick_types(info, meg='grad', ref_meg=False)) > 0:
        types.append('grad')

    ica = params['ica']
    data = np.dot(ica.mixing_matrix_[:, ic_idx].T,
                  ica.pca_components_[:ica.n_components_])
    data = np.atleast_2d(data)
    fig, axes = _prepare_trellis(len(types), max_col=3)
    for ch_idx, ch_type in enumerate(types):
        try:
            data_picks, pos, merge_grads, _, _ = _prepare_topo_plot(ica,
                                                                    ch_type,
                                                                    None)
        except Exception as exc:
            warn(exc)
            plt.close(fig)
            return
        this_data = data[:, data_picks]
        ax = axes[ch_idx]
        if merge_grads:
            from ..channels.layout import _merge_grad_data
        for ii, data_ in zip(ic_idx, this_data):
            ax.set_title('IC #%03d ' % ii + ch_type, fontsize=12)
            data_ = _merge_grad_data(data_) if merge_grads else data_
            plot_topomap(data_.flatten(), pos, axis=ax, show=False)
            ax.set_yticks([])
            ax.set_xticks([])
            ax.set_frame_on(False)
    tight_layout(fig=fig)
    fig.subplots_adjust(top=0.95)
    fig.canvas.draw()
    plt_show(True)