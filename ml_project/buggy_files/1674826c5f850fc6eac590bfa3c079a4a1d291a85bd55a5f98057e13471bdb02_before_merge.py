def read_ica_eeglab(fname):
    """Load ICA information saved in an EEGLAB .set file.

    Parameters
    ----------
    fname : str
        Complete path to a .set EEGLAB file that contains an ICA object.

    Returns
    -------
    ica : instance of ICA
        An ICA object based on the information contained in the input file.
    """
    eeg = _check_load_mat(fname, None)
    info = _get_info(eeg)[0]
    pick_info(info, np.round(eeg['icachansind']).astype(int) - 1, copy=False)

    n_components = eeg.icaweights.shape[0]

    ica = ICA(method='imported_eeglab', n_components=n_components)

    ica.current_fit = "eeglab"
    ica.ch_names = info["ch_names"]
    ica.n_pca_components = None
    ica.n_components_ = n_components

    ica.pre_whitener_ = np.ones((len(eeg.icachansind), 1))
    ica.pca_mean_ = np.zeros(len(eeg.icachansind))

    n_ch = len(ica.ch_names)
    assert eeg.icaweights.shape == (n_components, n_ch)
    # When PCA reduction is used in EEGLAB, runica returns
    # weights= weights*sphere*eigenvectors(:,1:ncomps)';
    # sphere = eye(urchans). When PCA reduction is not used, we have:
    #
    #     eeg.icawinv == pinv(eeg.icaweights @ eeg.icasphere)
    #
    # So in either case, we can use SVD to get our square whitened
    # weights matrix (u * s) and our PCA vectors (v) back:
    use = eeg.icaweights @ eeg.icasphere
    u, s, v = _safe_svd(use, full_matrices=False)
    ica.unmixing_matrix_ = u * s
    ica.pca_components_ = v
    ica.pca_explained_variance_ = s * s
    ica._update_mixing_matrix()
    return ica