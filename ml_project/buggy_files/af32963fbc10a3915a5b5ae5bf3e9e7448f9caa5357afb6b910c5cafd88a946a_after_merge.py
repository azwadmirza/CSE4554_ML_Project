def svd(a, full_matrices=True, compute_uv=True):
    """
    Singular Value Decomposition.

    Factors the matrix `a` as ``u * np.diag(s) * v``, where `u` and `v`
    are unitary and `s` is a 1-d array of `a`'s singular values.

    Parameters
    ----------
    a : (..., M, N) array_like
        A real or complex matrix of shape (`M`, `N`) .
    full_matrices : bool, optional
        If True (default), `u` and `v` have the shapes (`M`, `M`) and
        (`N`, `N`), respectively.  Otherwise, the shapes are (`M`, `K`)
        and (`K`, `N`), respectively, where `K` = min(`M`, `N`).
    compute_uv : bool, optional
        Whether or not to compute `u` and `v` in addition to `s`.  True
        by default.

    Returns
    -------
    u : { (..., M, M), (..., M, K) } array
        Unitary matrices. The actual shape depends on the value of
        ``full_matrices``. Only returned when ``compute_uv`` is True.
    s : (..., K) array
        The singular values for every matrix, sorted in descending order.
    v : { (..., N, N), (..., K, N) } array
        Unitary matrices. The actual shape depends on the value of
        ``full_matrices``. Only returned when ``compute_uv`` is True.

    Raises
    ------
    LinAlgError
        If SVD computation does not converge.

    Notes
    -----

    .. versionadded:: 1.8.0

    Broadcasting rules apply, see the `numpy.linalg` documentation for
    details.

    The decomposition is performed using LAPACK routine _gesdd

    The SVD is commonly written as ``a = U S V.H``.  The `v` returned
    by this function is ``V.H`` and ``u = U``.

    If ``U`` is a unitary matrix, it means that it
    satisfies ``U.H = inv(U)``.

    The rows of `v` are the eigenvectors of ``a.H a``. The columns
    of `u` are the eigenvectors of ``a a.H``.  For row ``i`` in
    `v` and column ``i`` in `u`, the corresponding eigenvalue is
    ``s[i]**2``.

    If `a` is a `matrix` object (as opposed to an `ndarray`), then so
    are all the return values.

    Examples
    --------
    >>> a = np.random.randn(9, 6) + 1j*np.random.randn(9, 6)

    Reconstruction based on full SVD:

    >>> U, s, V = np.linalg.svd(a, full_matrices=True)
    >>> U.shape, V.shape, s.shape
    ((9, 9), (6, 6), (6,))
    >>> S = np.zeros((9, 6), dtype=complex)
    >>> S[:6, :6] = np.diag(s)
    >>> np.allclose(a, np.dot(U, np.dot(S, V)))
    True

    Reconstruction based on reduced SVD:

    >>> U, s, V = np.linalg.svd(a, full_matrices=False)
    >>> U.shape, V.shape, s.shape
    ((9, 6), (6, 6), (6,))
    >>> S = np.diag(s)
    >>> np.allclose(a, np.dot(U, np.dot(S, V)))
    True

    """
    a, wrap = _makearray(a)
    _assertNoEmpty2d(a)
    _assertRankAtLeast2(a)
    t, result_t = _commonType(a)

    extobj = get_linalg_error_extobj(_raise_linalgerror_svd_nonconvergence)

    m = a.shape[-2]
    n = a.shape[-1]
    if compute_uv:
        if full_matrices:
            if m < n:
                gufunc = _umath_linalg.svd_m_f
            else:
                gufunc = _umath_linalg.svd_n_f
        else:
            if m < n:
                gufunc = _umath_linalg.svd_m_s
            else:
                gufunc = _umath_linalg.svd_n_s

        signature = 'D->DdD' if isComplexType(t) else 'd->ddd'
        u, s, vt = gufunc(a, signature=signature, extobj=extobj)
        u = u.astype(result_t, copy=False)
        s = s.astype(_realType(result_t), copy=False)
        vt = vt.astype(result_t, copy=False)
        return wrap(u), s, wrap(vt)
    else:
        if m < n:
            gufunc = _umath_linalg.svd_m
        else:
            gufunc = _umath_linalg.svd_n

        signature = 'D->d' if isComplexType(t) else 'd->d'
        s = gufunc(a, signature=signature, extobj=extobj)
        s = s.astype(_realType(result_t), copy=False)
        return s