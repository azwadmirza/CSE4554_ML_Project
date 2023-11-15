def _determine_method(reference, configuration, max_cutoff, min_cutoff=None,
                      box=None, method=None):
    """Guesses the fastest method for capped distance calculations based on the
    size of the coordinate sets and the relative size of the target volume.

    Parameters
    ----------
    reference : numpy.ndarray
        Reference coordinate array with shape ``(3,)`` or ``(n, 3)``.
    configuration : numpy.ndarray
        Configuration coordinate array with shape ``(3,)`` or ``(m, 3)``.
    max_cutoff : float
        Maximum cutoff distance between `reference` and `configuration`
        coordinates.
    min_cutoff : float, optional
        Minimum cutoff distance between `reference` and `configuration`
        coordinates.
    box : numpy.ndarray, None (default None)
        The unitcell dimensions of the system, which can be orthogonal or
        triclinic and must be provided in the same format as returned by
        :attr:`MDAnalysis.coordinates.base.Timestep.dimensions`:\n
        ``[lx, ly, lz, alpha, beta, gamma]``.
    method : {'bruteforce', 'nsgrid', 'pkdtree', None} (default None)
        Keyword to override the automatic guessing of the employed search
        method.

    Returns
    -------
    function : callable
        The function implementing the guessed (or deliberatly chosen) method.
    """
    methods = {'bruteforce': _bruteforce_capped,
               'pkdtree': _pkdtree_capped,
               'nsgrid': _nsgrid_capped}

    if method is not None:
        return methods[method.lower()]

    if len(reference) < 10 or len(configuration) < 10:
        return methods['bruteforce']
    elif len(reference) * len(configuration) >= 1e8:
        # CAUTION : for large datasets, shouldnt go into 'bruteforce'
        # in any case. Arbitrary number, but can be characterized
        return methods['nsgrid']
    else:
        if box is None:
            min_dim = np.array([reference.min(axis=0),
                                configuration.min(axis=0)])
            max_dim = np.array([reference.max(axis=0),
                                configuration.max(axis=0)])
            size = max_dim.max(axis=0) - min_dim.min(axis=0)
        elif np.all(box[3:] == 90.0):
            size = box[:3]
        else:
            tribox = triclinic_vectors(box)
            size = tribox.max(axis=0) - tribox.min(axis=0)
        if np.any(max_cutoff > 0.3*size):
            return methods['bruteforce']
        else:
            return methods['nsgrid']