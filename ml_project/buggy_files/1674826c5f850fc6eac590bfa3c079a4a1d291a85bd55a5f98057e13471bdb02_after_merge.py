def read_ica_eeglab(fname, *, verbose=None):
    """Load ICA information saved in an EEGLAB .set file.

    Parameters
    ----------
    fname : str
        Complete path to a .set EEGLAB file that contains an ICA object.
    %(verbose)s

    Returns
    -------
    ica : instance of ICA
        An ICA object based on the information contained in the input file.
    """
    eeg = _check_load_mat(fname, None)
    info, eeg_montage, _ = _get_info(eeg)
    info.set_montage(eeg_montage)
    pick_info(info, np.round(eeg['icachansind']).astype(int) - 1, copy=False)

    rank = eeg.icasphere.shape[0]
    n_components = eeg.icaweights.shape[0]

    ica = ICA(method='imported_eeglab', n_components=n_components)

    ica.current_fit = "eeglab"
    ica.ch_names = info["ch_names"]
    ica.n_pca_components = None
    ica.n_components_ = n_components

    n_ch = len(ica.ch_names)
    assert len(eeg.icachansind) == n_ch

    ica.pre_whitener_ = np.ones((n_ch, 1))
    ica.pca_mean_ = np.zeros(n_ch)

    assert eeg.icasphere.shape[1] == n_ch
    assert eeg.icaweights.shape == (n_components, rank)

    # When PCA reduction is used in EEGLAB, runica returns
    # weights= weights*sphere*eigenvectors(:,1:ncomps)';
    # sphere = eye(urchans). When PCA reduction is not used, we have:
    #
    #     eeg.icawinv == pinv(eeg.icaweights @ eeg.icasphere)
    #
    # So in either case, we can use SVD to get our square whitened
    # weights matrix (u * s) and our PCA vectors (v) back:
    use = eeg.icaweights @ eeg.icasphere
    use_check = linalg.pinv(eeg.icawinv)
    if not np.allclose(use, use_check, rtol=1e-6):
        warn('Mismatch between icawinv and icaweights @ icasphere from EEGLAB '
             'possibly due to ICA component removal, assuming icawinv is '
             'correct')
        use = use_check
    u, s, v = _safe_svd(use, full_matrices=False)
    ica.unmixing_matrix_ = u * s
    ica.pca_components_ = v
    ica.pca_explained_variance_ = s * s
    ica.info = info
    ica._update_mixing_matrix()
    ica._update_ica_names()
    return ica