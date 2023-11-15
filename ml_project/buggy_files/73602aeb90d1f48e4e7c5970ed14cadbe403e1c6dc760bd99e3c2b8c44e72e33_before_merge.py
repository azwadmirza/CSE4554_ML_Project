def _prepare_connectivity(epoch_block, tmin, tmax, fmin, fmax, sfreq, indices,
                          mode, fskip, n_bands,
                          cwt_freqs, faverage):
    """Check and precompute dimensions of results data."""
    rfftfreq = _import_fft('rfftfreq')
    first_epoch = epoch_block[0]

    # get the data size and time scale
    n_signals, n_times_in, times_in = _get_and_verify_data_sizes(first_epoch)

    if times_in is None:
        # we are not using Epochs or SourceEstimate(s) as input
        times_in = np.linspace(0.0, n_times_in / sfreq, n_times_in,
                               endpoint=False)

    n_times_in = len(times_in)
    mask = _time_mask(times_in, tmin, tmax, sfreq=sfreq)
    tmin_idx, tmax_idx = np.where(mask)[0][[0, -1]]
    tmax_idx += 1
    tmin_true = times_in[tmin_idx]
    tmax_true = times_in[tmax_idx - 1]  # time of last point used

    times = times_in[tmin_idx:tmax_idx]
    n_times = len(times)

    if indices is None:
        logger.info('only using indices for lower-triangular matrix')
        # only compute r for lower-triangular region
        indices_use = np.tril_indices(n_signals, -1)
    else:
        indices_use = check_indices(indices)

    # number of connectivities to compute
    n_cons = len(indices_use[0])

    logger.info('    computing connectivity for %d connections'
                % n_cons)
    logger.info('    using t=%0.3fs..%0.3fs for estimation (%d points)'
                % (tmin_true, tmax_true, n_times))

    # get frequencies of interest for the different modes
    if mode in ('multitaper', 'fourier'):
        # fmin fmax etc is only supported for these modes
        # decide which frequencies to keep
        freqs_all = rfftfreq(n_times, 1. / sfreq)
    elif mode == 'cwt_morlet':
        # cwt_morlet mode
        if cwt_freqs is None:
            raise ValueError('define frequencies of interest using '
                             'cwt_freqs')
        else:
            cwt_freqs = cwt_freqs.astype(np.float64)
        if any(cwt_freqs > (sfreq / 2.)):
            raise ValueError('entries in cwt_freqs cannot be '
                             'larger than Nyquist (sfreq / 2)')
        freqs_all = cwt_freqs
    else:
        raise ValueError('mode has an invalid value')

    # check that fmin corresponds to at least 5 cycles
    dur = float(n_times) / sfreq
    five_cycle_freq = 5. / dur
    if len(fmin) == 1 and fmin[0] == -np.inf:
        # we use the 5 cycle freq. as default
        fmin = np.array([five_cycle_freq])
    else:
        if np.any(fmin < five_cycle_freq):
            warn('fmin=%0.3f Hz corresponds to %0.3f < 5 cycles '
                 'based on the epoch length %0.3f sec, need at least %0.3f '
                 'sec epochs or fmin=%0.3f. Spectrum estimate will be '
                 'unreliable.' % (np.min(fmin), dur * np.min(fmin), dur,
                                  5. / np.min(fmin), five_cycle_freq))

    # create a frequency mask for all bands
    freq_mask = np.zeros(len(freqs_all), dtype=bool)
    for f_lower, f_upper in zip(fmin, fmax):
        freq_mask |= ((freqs_all >= f_lower) & (freqs_all <= f_upper))

    # possibly skip frequency points
    for pos in range(fskip):
        freq_mask[pos + 1::fskip + 1] = False

    # the frequency points where we compute connectivity
    freqs = freqs_all[freq_mask]
    n_freqs = len(freqs)

    # get the freq. indices and points for each band
    freq_idx_bands = [np.where((freqs >= fl) & (freqs <= fu))[0]
                      for fl, fu in zip(fmin, fmax)]
    freqs_bands = [freqs[freq_idx] for freq_idx in freq_idx_bands]

    # make sure we don't have empty bands
    for i, n_f_band in enumerate([len(f) for f in freqs_bands]):
        if n_f_band == 0:
            raise ValueError('There are no frequency points between '
                             '%0.1fHz and %0.1fHz. Change the band '
                             'specification (fmin, fmax) or the '
                             'frequency resolution.'
                             % (fmin[i], fmax[i]))
    if n_bands == 1:
        logger.info('    frequencies: %0.1fHz..%0.1fHz (%d points)'
                    % (freqs_bands[0][0], freqs_bands[0][-1],
                       n_freqs))
    else:
        logger.info('    computing connectivity for the bands:')
        for i, bfreqs in enumerate(freqs_bands):
            logger.info('     band %d: %0.1fHz..%0.1fHz '
                        '(%d points)' % (i + 1, bfreqs[0],
                                         bfreqs[-1], len(bfreqs)))
    if faverage:
        logger.info('    connectivity scores will be averaged for '
                    'each band')

    return (n_cons, times, n_times, times_in, n_times_in, tmin_idx,
            tmax_idx, n_freqs, freq_mask, freqs, freqs_bands, freq_idx_bands,
            n_signals, indices_use)