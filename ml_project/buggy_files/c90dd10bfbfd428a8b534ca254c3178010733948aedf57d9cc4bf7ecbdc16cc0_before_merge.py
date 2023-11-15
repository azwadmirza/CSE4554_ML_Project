def spectral_connectivity(data, method='coh', indices=None, sfreq=2 * np.pi,
                          mode='multitaper', fmin=None, fmax=np.inf,
                          fskip=0, faverage=False, tmin=None, tmax=None,
                          mt_bandwidth=None, mt_adaptive=False,
                          mt_low_bias=True, cwt_freqs=None,
                          cwt_n_cycles=7, block_size=1000, n_jobs=1,
                          verbose=None):
    """Compute frequency- and time-frequency-domain connectivity measures.

    The connectivity method(s) are specified using the "method" parameter.
    All methods are based on estimates of the cross- and power spectral
    densities (CSD/PSD) Sxy and Sxx, Syy.

    Parameters
    ----------
    data : array-like, shape=(n_epochs, n_signals, n_times) | Epochs
        The data from which to compute connectivity. Note that it is also
        possible to combine multiple signals by providing a list of tuples,
        e.g., data = [(arr_0, stc_0), (arr_1, stc_1), (arr_2, stc_2)],
        corresponds to 3 epochs, and arr_* could be an array with the same
        number of time points as stc_*. The array-like object can also
        be a list/generator of array, shape =(n_signals, n_times),
        or a list/generator of SourceEstimate or VolSourceEstimate objects.
    method : str | list of str
        Connectivity measure(s) to compute.
    indices : tuple of array | None
        Two arrays with indices of connections for which to compute
        connectivity. If None, all connections are computed.
    sfreq : float
        The sampling frequency.
    mode : str
        Spectrum estimation mode can be either: 'multitaper', 'fourier', or
        'cwt_morlet'.
    fmin : float | tuple of float
        The lower frequency of interest. Multiple bands are defined using
        a tuple, e.g., (8., 20.) for two bands with 8Hz and 20Hz lower freq.
        If None the frequency corresponding to an epoch length of 5 cycles
        is used.
    fmax : float | tuple of float
        The upper frequency of interest. Multiple bands are dedined using
        a tuple, e.g. (13., 30.) for two band with 13Hz and 30Hz upper freq.
    fskip : int
        Omit every "(fskip + 1)-th" frequency bin to decimate in frequency
        domain.
    faverage : bool
        Average connectivity scores for each frequency band. If True,
        the output freqs will be a list with arrays of the frequencies
        that were averaged.
    tmin : float | None
        Time to start connectivity estimation. Note: when "data" is an array,
        the first sample is assumed to be at time 0. For other types
        (Epochs, etc.), the time information contained in the object is used
        to compute the time indices.
    tmax : float | None
        Time to end connectivity estimation. Note: when "data" is an array,
        the first sample is assumed to be at time 0. For other types
        (Epochs, etc.), the time information contained in the object is used
        to compute the time indices.
    mt_bandwidth : float | None
        The bandwidth of the multitaper windowing function in Hz.
        Only used in 'multitaper' mode.
    mt_adaptive : bool
        Use adaptive weights to combine the tapered spectra into PSD.
        Only used in 'multitaper' mode.
    mt_low_bias : bool
        Only use tapers with more than 90%% spectral concentration within
        bandwidth. Only used in 'multitaper' mode.
    cwt_freqs : array
        Array of frequencies of interest. Only used in 'cwt_morlet' mode.
    cwt_n_cycles : float | array of float
        Number of cycles. Fixed number or one per frequency. Only used in
        'cwt_morlet' mode.
    block_size : int
        How many connections to compute at once (higher numbers are faster
        but require more memory).
    n_jobs : int
        How many epochs to process in parallel.
    %(verbose)s

    Returns
    -------
    con : array | list of array
        Computed connectivity measure(s). The shape of each array is either
        (n_signals, n_signals, n_freqs) mode: 'multitaper' or 'fourier'
        (n_signals, n_signals, n_freqs, n_times) mode: 'cwt_morlet'
        when "indices" is None, or
        (n_con, n_freqs) mode: 'multitaper' or 'fourier'
        (n_con, n_freqs, n_times) mode: 'cwt_morlet'
        when "indices" is specified and "n_con = len(indices[0])".
    freqs : array
        Frequency points at which the connectivity was computed.
    times : array
        Time points for which the connectivity was computed.
    n_epochs : int
        Number of epochs used for computation.
    n_tapers : int
        The number of DPSS tapers used. Only defined in 'multitaper' mode.
        Otherwise None is returned.

    Notes
    -----
    The spectral densities can be estimated using a multitaper method with
    digital prolate spheroidal sequence (DPSS) windows, a discrete Fourier
    transform with Hanning windows, or a continuous wavelet transform using
    Morlet wavelets. The spectral estimation mode is specified using the
    "mode" parameter.

    By default, the connectivity between all signals is computed (only
    connections corresponding to the lower-triangular part of the
    connectivity matrix). If one is only interested in the connectivity
    between some signals, the "indices" parameter can be used. For example,
    to compute the connectivity between the signal with index 0 and signals
    "2, 3, 4" (a total of 3 connections) one can use the following::

        indices = (np.array([0, 0, 0]),    # row indices
                   np.array([2, 3, 4]))    # col indices

        con_flat = spectral_connectivity(data, method='coh',
                                         indices=indices, ...)

    In this case con_flat.shape = (3, n_freqs). The connectivity scores are
    in the same order as defined indices.

    **Supported Connectivity Measures**

    The connectivity method(s) is specified using the "method" parameter. The
    following methods are supported (note: ``E[]`` denotes average over
    epochs). Multiple measures can be computed at once by using a list/tuple,
    e.g., ``['coh', 'pli']`` to compute coherence and PLI.

        'coh' : Coherence given by::

                     | E[Sxy] |
            C = ---------------------
                sqrt(E[Sxx] * E[Syy])

        'cohy' : Coherency given by::

                       E[Sxy]
            C = ---------------------
                sqrt(E[Sxx] * E[Syy])

        'imcoh' : Imaginary coherence [1]_ given by::

                      Im(E[Sxy])
            C = ----------------------
                sqrt(E[Sxx] * E[Syy])

        'plv' : Phase-Locking Value (PLV) [2]_ given by::

            PLV = |E[Sxy/|Sxy|]|

        'ciplv' : corrected imaginary PLV (icPLV) [3]_ given by::

                             |E[Im(Sxy/|Sxy|)]|
            ciPLV = ------------------------------------
                     sqrt(1 - |E[real(Sxy/|Sxy|)]| ** 2)

        'ppc' : Pairwise Phase Consistency (PPC), an unbiased estimator
        of squared PLV [4]_.

        'pli' : Phase Lag Index (PLI) [5]_ given by::

            PLI = |E[sign(Im(Sxy))]|

        'pli2_unbiased' : Unbiased estimator of squared PLI [6]_.

        'wpli' : Weighted Phase Lag Index (WPLI) [6]_ given by::

                      |E[Im(Sxy)]|
            WPLI = ------------------
                      E[|Im(Sxy)|]

        'wpli2_debiased' : Debiased estimator of squared WPLI [6]_.

    References
    ----------
    .. [1] Nolte et al. "Identifying true brain interaction from EEG data using
           the imaginary part of coherency" Clinical neurophysiology, vol. 115,
           no. 10, pp. 2292-2307, Oct. 2004.
    .. [2] Lachaux et al. "Measuring phase synchrony in brain signals" Human
           brain mapping, vol. 8, no. 4, pp. 194-208, Jan. 1999.
    .. [3] Bruña et al. "Phase locking value revisited: teaching new tricks to
           an old dog" Journal of Neural Engineering, vol. 15, no. 5, pp.
           056011 , Jul. 2018.
    .. [4] Vinck et al. "The pairwise phase consistency: a bias-free measure of
           rhythmic neuronal synchronization" NeuroImage, vol. 51, no. 1,
           pp. 112-122, May 2010.
    .. [5] Stam et al. "Phase lag index: assessment of functional connectivity
           from multi channel EEG and MEG with diminished bias from common
           sources" Human brain mapping, vol. 28, no. 11, pp. 1178-1193,
           Nov. 2007.
    .. [6] Vinck et al. "An improved index of phase-synchronization for
           electro-physiological data in the presence of volume-conduction,
           noise and sample-size bias" NeuroImage, vol. 55, no. 4,
           pp. 1548-1565, Apr. 2011.
    """
    if n_jobs != 1:
        parallel, my_epoch_spectral_connectivity, _ = \
            parallel_func(_epoch_spectral_connectivity, n_jobs,
                          verbose=verbose)

    # format fmin and fmax and check inputs
    if fmin is None:
        fmin = -np.inf  # set it to -inf, so we can adjust it later

    fmin = np.array((fmin,), dtype=float).ravel()
    fmax = np.array((fmax,), dtype=float).ravel()
    if len(fmin) != len(fmax):
        raise ValueError('fmin and fmax must have the same length')
    if np.any(fmin > fmax):
        raise ValueError('fmax must be larger than fmin')

    n_bands = len(fmin)

    # assign names to connectivity methods
    if not isinstance(method, (list, tuple)):
        method = [method]  # make it a list so we can iterate over it

    # handle connectivity estimators
    (con_method_types, n_methods, accumulate_psd,
     n_comp_args) = _check_estimators(method=method, mode=mode)

    if isinstance(data, BaseEpochs):
        times_in = data.times  # input times for Epochs input type
        sfreq = data.info['sfreq']

    # loop over data; it could be a generator that returns
    # (n_signals x n_times) arrays or SourceEstimates
    epoch_idx = 0
    logger.info('Connectivity computation...')
    for epoch_block in _get_n_epochs(data, n_jobs):
        if epoch_idx == 0:
            # initialize everything times and frequencies
            (n_cons, times, n_times, times_in, n_times_in, tmin_idx,
             tmax_idx, n_freqs, freq_mask, freqs, freqs_bands, freq_idx_bands,
             n_signals, indices_use) = _prepare_connectivity(
                epoch_block=epoch_block, tmin=tmin, tmax=tmax, fmin=fmin,
                fmax=fmax, sfreq=sfreq, indices=indices, mode=mode,
                fskip=fskip, n_bands=n_bands,
                cwt_freqs=cwt_freqs, faverage=faverage)

            # get the window function, wavelets, etc for different modes
            (spectral_params, mt_adaptive, n_times_spectrum,
             n_tapers) = _assemble_spectral_params(
                mode=mode, n_times=n_times, mt_adaptive=mt_adaptive,
                mt_bandwidth=mt_bandwidth, sfreq=sfreq,
                mt_low_bias=mt_low_bias, cwt_n_cycles=cwt_n_cycles,
                cwt_freqs=cwt_freqs, freqs=freqs, freq_mask=freq_mask)

            # unique signals for which we actually need to compute PSD etc.
            sig_idx = np.unique(np.r_[indices_use[0], indices_use[1]])

            # map indices to unique indices
            idx_map = [np.searchsorted(sig_idx, ind) for ind in indices_use]

            # allocate space to accumulate PSD
            if accumulate_psd:
                if n_times_spectrum == 0:
                    psd_shape = (len(sig_idx), n_freqs)
                else:
                    psd_shape = (len(sig_idx), n_freqs, n_times_spectrum)
                psd = np.zeros(psd_shape)
            else:
                psd = None

            # create instances of the connectivity estimators
            con_methods = [mtype(n_cons, n_freqs, n_times_spectrum)
                           for mtype in con_method_types]

            sep = ', '
            metrics_str = sep.join([meth.name for meth in con_methods])
            logger.info('    the following metrics will be computed: %s'
                        % metrics_str)

        # check dimensions and time scale
        for this_epoch in epoch_block:
            _get_and_verify_data_sizes(this_epoch, n_signals, n_times_in,
                                       times_in)

        call_params = dict(
            sig_idx=sig_idx, tmin_idx=tmin_idx,
            tmax_idx=tmax_idx, sfreq=sfreq, mode=mode,
            freq_mask=freq_mask, idx_map=idx_map, block_size=block_size,
            psd=psd, accumulate_psd=accumulate_psd,
            mt_adaptive=mt_adaptive,
            con_method_types=con_method_types,
            con_methods=con_methods if n_jobs == 1 else None,
            n_signals=n_signals, n_times=n_times,
            accumulate_inplace=True if n_jobs == 1 else False)
        call_params.update(**spectral_params)

        if n_jobs == 1:
            # no parallel processing
            for this_epoch in epoch_block:
                logger.info('    computing connectivity for epoch %d'
                            % (epoch_idx + 1))
                # con methods and psd are updated inplace
                _epoch_spectral_connectivity(data=this_epoch, **call_params)
                epoch_idx += 1
        else:
            # process epochs in parallel
            logger.info('    computing connectivity for epochs %d..%d'
                        % (epoch_idx + 1, epoch_idx + len(epoch_block)))

            out = parallel(my_epoch_spectral_connectivity(
                           data=this_epoch, **call_params)
                           for this_epoch in epoch_block)
            # do the accumulation
            for this_out in out:
                for method, parallel_method in zip(con_methods, this_out[0]):
                    method.combine(parallel_method)
                if accumulate_psd:
                    psd += this_out[1]

            epoch_idx += len(epoch_block)

    # normalize
    n_epochs = epoch_idx
    if accumulate_psd:
        psd /= n_epochs

    # compute final connectivity scores
    con = list()
    for method, n_args in zip(con_methods, n_comp_args):
        # future estimators will need to be handled here
        if n_args == 3:
            # compute all scores at once
            method.compute_con(slice(0, n_cons), n_epochs)
        elif n_args == 5:
            # compute scores block-wise to save memory
            for i in range(0, n_cons, block_size):
                con_idx = slice(i, i + block_size)
                psd_xx = psd[idx_map[0][con_idx]]
                psd_yy = psd[idx_map[1][con_idx]]
                method.compute_con(con_idx, n_epochs, psd_xx, psd_yy)
        else:
            raise RuntimeError('This should never happen.')

        # get the connectivity scores
        this_con = method.con_scores

        if this_con.shape[0] != n_cons:
            raise ValueError('First dimension of connectivity scores must be '
                             'the same as the number of connections')
        if faverage:
            if this_con.shape[1] != n_freqs:
                raise ValueError('2nd dimension of connectivity scores must '
                                 'be the same as the number of frequencies')
            con_shape = (n_cons, n_bands) + this_con.shape[2:]
            this_con_bands = np.empty(con_shape, dtype=this_con.dtype)
            for band_idx in range(n_bands):
                this_con_bands[:, band_idx] =\
                    np.mean(this_con[:, freq_idx_bands[band_idx]], axis=1)
            this_con = this_con_bands

        con.append(this_con)

    if indices is None:
        # return all-to-all connectivity matrices
        logger.info('    assembling connectivity matrix '
                    '(filling the upper triangular region of the matrix)')
        con_flat = con
        con = list()
        for this_con_flat in con_flat:
            this_con = np.zeros((n_signals, n_signals) +
                                this_con_flat.shape[1:],
                                dtype=this_con_flat.dtype)
            this_con[indices_use] = this_con_flat
            con.append(this_con)

    logger.info('[Connectivity computation done]')

    if n_methods == 1:
        # for a single method return connectivity directly
        con = con[0]

    if faverage:
        # for each band we return the frequencies that were averaged
        freqs = freqs_bands

    return con, freqs, times, n_epochs, n_tapers