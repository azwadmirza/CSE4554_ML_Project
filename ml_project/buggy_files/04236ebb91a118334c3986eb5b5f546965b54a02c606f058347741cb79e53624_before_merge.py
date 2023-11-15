def _plot_psd(inst, fig, freqs, psd_list, picks_list, titles_list,
              units_list, scalings_list, ax_list, make_label, color, area_mode,
              area_alpha, dB, estimate, average, spatial_colors, xscale,
              line_alpha, sphere):
    # helper function for plot_raw_psd and plot_epochs_psd
    from matplotlib.ticker import ScalarFormatter
    from .evoked import _plot_lines
    sphere = _check_sphere(sphere, inst.info)

    for key, ls in zip(['lowpass', 'highpass', 'line_freq'],
                       ['--', '--', '-.']):
        if inst.info[key] is not None:
            for ax in ax_list:
                ax.axvline(inst.info[key], color='k', linestyle=ls,
                           alpha=0.25, linewidth=2, zorder=2)
    if line_alpha is None:
        line_alpha = 1.0 if average else 0.75
    line_alpha = float(line_alpha)
    ylabels = list()
    for ii, (psd, picks, title, ax, scalings, units) in enumerate(zip(
            psd_list, picks_list, titles_list, ax_list,
            scalings_list, units_list)):
        ylabel = _convert_psds(psd, dB, estimate, scalings, units,
                               [inst.ch_names[pi] for pi in picks])
        ylabels.append(ylabel)
        del ylabel

        if average:
            # mean across channels
            psd_mean = np.mean(psd, axis=0)
            if area_mode == 'std':
                # std across channels
                psd_std = np.std(psd, axis=0)
                hyp_limits = (psd_mean - psd_std, psd_mean + psd_std)
            elif area_mode == 'range':
                hyp_limits = (np.min(psd, axis=0),
                              np.max(psd, axis=0))
            else:  # area_mode is None
                hyp_limits = None

            ax.plot(freqs, psd_mean, color=color, alpha=line_alpha,
                    linewidth=0.5)
            if hyp_limits is not None:
                ax.fill_between(freqs, hyp_limits[0], y2=hyp_limits[1],
                                color=color, alpha=area_alpha)

    if not average:
        picks = np.concatenate(picks_list)
        psd_list = np.concatenate(psd_list)
        types = np.array([channel_type(inst.info, idx) for idx in picks])
        # Needed because the data do not match the info anymore.
        info = create_info([inst.ch_names[p] for p in picks],
                           inst.info['sfreq'], types)
        info['chs'] = [inst.info['chs'][p] for p in picks]
        valid_channel_types = [
            'mag', 'grad', 'eeg', 'csd', 'seeg', 'eog', 'ecg',
            'emg', 'dipole', 'gof', 'bio', 'ecog', 'hbo',
            'hbr', 'misc', 'fnirs_raw', 'fnirs_od']
        ch_types_used = list()
        for this_type in valid_channel_types:
            if this_type in types:
                ch_types_used.append(this_type)
        assert len(ch_types_used) == len(ax_list)
        unit = ''
        units = {t: yl for t, yl in zip(ch_types_used, ylabels)}
        titles = {c: t for c, t in zip(ch_types_used, titles_list)}
        picks = np.arange(len(psd_list))
        if not spatial_colors:
            spatial_colors = color
        _plot_lines(psd_list, info, picks, fig, ax_list, spatial_colors,
                    unit, units=units, scalings=None, hline=None, gfp=False,
                    types=types, zorder='std', xlim=(freqs[0], freqs[-1]),
                    ylim=None, times=freqs, bad_ch_idx=[], titles=titles,
                    ch_types_used=ch_types_used, selectable=True, psd=True,
                    line_alpha=line_alpha, nave=None, time_unit='ms',
                    sphere=sphere)
    for ii, ax in enumerate(ax_list):
        ax.grid(True, linestyle=':')
        if xscale == 'log':
            ax.set(xscale='log')
            ax.set(xlim=[freqs[1] if freqs[0] == 0 else freqs[0], freqs[-1]])
            ax.get_xaxis().set_major_formatter(ScalarFormatter())
        else:
            ax.set(xlim=(freqs[0], freqs[-1]))
        if make_label:
            if ii == len(picks_list) - 1:
                ax.set_xlabel('Frequency (Hz)')
            ax.set(ylabel=ylabels[ii], title=titles_list[ii])
    if make_label:
        fig.subplots_adjust(left=.1, bottom=.1, right=.9, top=.9, wspace=0.3,
                            hspace=0.5)
    return fig