def eigs(A, k=6, M=None, sigma=None, which='LM', v0=None,
         ncv=None, maxiter=None, tol=0, return_eigenvectors=True,
         Minv=None, OPinv=None, OPpart=None):
    """
    Find k eigenvalues and eigenvectors of the square matrix A.

    Solves ``A * x[i] = w[i] * x[i]``, the standard eigenvalue problem
    for w[i] eigenvalues with corresponding eigenvectors x[i].

    If M is specified, solves ``A * x[i] = w[i] * M * x[i]``, the
    generalized eigenvalue problem for w[i] eigenvalues
    with corresponding eigenvectors x[i]

    Parameters
    ----------
    A : ndarray, sparse matrix or LinearOperator
        An array, sparse matrix, or LinearOperator representing
        the operation ``A * x``, where A is a real or complex square matrix.
    k : int, optional
        The number of eigenvalues and eigenvectors desired.
        `k` must be smaller than N-1. It is not possible to compute all
        eigenvectors of a matrix.
    M : ndarray, sparse matrix or LinearOperator, optional
        An array, sparse matrix, or LinearOperator representing
        the operation M*x for the generalized eigenvalue problem

            A * x = w * M * x.

        M must represent a real, symmetric matrix if A is real, and must
        represent a complex, hermitian matrix if A is complex. For best
        results, the data type of M should be the same as that of A.
        Additionally:

            If `sigma` is None, M is positive definite

            If sigma is specified, M is positive semi-definite

        If sigma is None, eigs requires an operator to compute the solution
        of the linear equation ``M * x = b``.  This is done internally via a
        (sparse) LU decomposition for an explicit matrix M, or via an
        iterative solver for a general linear operator.  Alternatively,
        the user can supply the matrix or operator Minv, which gives
        ``x = Minv * b = M^-1 * b``.
    sigma : real or complex, optional
        Find eigenvalues near sigma using shift-invert mode.  This requires
        an operator to compute the solution of the linear system
        ``[A - sigma * M] * x = b``, where M is the identity matrix if
        unspecified. This is computed internally via a (sparse) LU
        decomposition for explicit matrices A & M, or via an iterative
        solver if either A or M is a general linear operator.
        Alternatively, the user can supply the matrix or operator OPinv,
        which gives ``x = OPinv * b = [A - sigma * M]^-1 * b``.
        For a real matrix A, shift-invert can either be done in imaginary
        mode or real mode, specified by the parameter OPpart ('r' or 'i').
        Note that when sigma is specified, the keyword 'which' (below)
        refers to the shifted eigenvalues ``w'[i]`` where:

            If A is real and OPpart == 'r' (default),
              ``w'[i] = 1/2 * [1/(w[i]-sigma) + 1/(w[i]-conj(sigma))]``.

            If A is real and OPpart == 'i',
              ``w'[i] = 1/2i * [1/(w[i]-sigma) - 1/(w[i]-conj(sigma))]``.

            If A is complex, ``w'[i] = 1/(w[i]-sigma)``.

    v0 : ndarray, optional
        Starting vector for iteration.
        Default: random
    ncv : int, optional
        The number of Lanczos vectors generated
        `ncv` must be greater than `k`; it is recommended that ``ncv > 2*k``.
        Default: ``min(n, max(2*k + 1, 20))``
    which : str, ['LM' | 'SM' | 'LR' | 'SR' | 'LI' | 'SI'], optional
        Which `k` eigenvectors and eigenvalues to find:

            'LM' : largest magnitude

            'SM' : smallest magnitude

            'LR' : largest real part

            'SR' : smallest real part

            'LI' : largest imaginary part

            'SI' : smallest imaginary part

        When sigma != None, 'which' refers to the shifted eigenvalues w'[i]
        (see discussion in 'sigma', above).  ARPACK is generally better
        at finding large values than small values.  If small eigenvalues are
        desired, consider using shift-invert mode for better performance.
    maxiter : int, optional
        Maximum number of Arnoldi update iterations allowed
        Default: ``n*10``
    tol : float, optional
        Relative accuracy for eigenvalues (stopping criterion)
        The default value of 0 implies machine precision.
    return_eigenvectors : bool, optional
        Return eigenvectors (True) in addition to eigenvalues
    Minv : ndarray, sparse matrix or LinearOperator, optional
        See notes in M, above.
    OPinv : ndarray, sparse matrix or LinearOperator, optional
        See notes in sigma, above.
    OPpart : {'r' or 'i'}, optional
        See notes in sigma, above

    Returns
    -------
    w : ndarray
        Array of k eigenvalues.
    v : ndarray
        An array of `k` eigenvectors.
        ``v[:, i]`` is the eigenvector corresponding to the eigenvalue w[i].

    Raises
    ------
    ArpackNoConvergence
        When the requested convergence is not obtained.
        The currently converged eigenvalues and eigenvectors can be found
        as ``eigenvalues`` and ``eigenvectors`` attributes of the exception
        object.

    See Also
    --------
    eigsh : eigenvalues and eigenvectors for symmetric matrix A
    svds : singular value decomposition for a matrix A

    Notes
    -----
    This function is a wrapper to the ARPACK [1]_ SNEUPD, DNEUPD, CNEUPD,
    ZNEUPD, functions which use the Implicitly Restarted Arnoldi Method to
    find the eigenvalues and eigenvectors [2]_.

    References
    ----------
    .. [1] ARPACK Software, http://www.caam.rice.edu/software/ARPACK/
    .. [2] R. B. Lehoucq, D. C. Sorensen, and C. Yang,  ARPACK USERS GUIDE:
       Solution of Large Scale Eigenvalue Problems by Implicitly Restarted
       Arnoldi Methods. SIAM, Philadelphia, PA, 1998.

    Examples
    --------
    Find 6 eigenvectors of the identity matrix:

    >>> import scipy.sparse as sparse
    >>> id = np.eye(13)
    >>> vals, vecs = sparse.linalg.eigs(id, k=6)
    >>> vals
    array([ 1.+0.j,  1.+0.j,  1.+0.j,  1.+0.j,  1.+0.j,  1.+0.j])
    >>> vecs.shape
    (13, 6)

    """
    if A.shape[0] != A.shape[1]:
        raise ValueError('expected square matrix (shape=%s)' % (A.shape,))
    if M is not None:
        if M.shape != A.shape:
            raise ValueError('wrong M dimensions %s, should be %s'
                             % (M.shape, A.shape))
        if np.dtype(M.dtype).char.lower() != np.dtype(A.dtype).char.lower():
            import warnings
            warnings.warn('M does not have the same type precision as A. '
                          'This may adversely affect ARPACK convergence')
    n = A.shape[0]

    if k <= 0 or k >= n:
        raise ValueError("k=%d must be between 1 and ndim(A)-1=%d"
                         % (k, n - 1))

    if sigma is None:
        matvec = _aslinearoperator_with_dtype(A).matvec

        if OPinv is not None:
            raise ValueError("OPinv should not be specified "
                             "with sigma = None.")
        if OPpart is not None:
            raise ValueError("OPpart should not be specified with "
                             "sigma = None or complex A")

        if M is None:
            #standard eigenvalue problem
            mode = 1
            M_matvec = None
            Minv_matvec = None
            if Minv is not None:
                raise ValueError("Minv should not be "
                                 "specified with M = None.")
        else:
            #general eigenvalue problem
            mode = 2
            if Minv is None:
                Minv_matvec = get_inv_matvec(M, symmetric=True, tol=tol)
            else:
                Minv = _aslinearoperator_with_dtype(Minv)
                Minv_matvec = Minv.matvec
            M_matvec = _aslinearoperator_with_dtype(M).matvec
    else:
        #sigma is not None: shift-invert mode
        if np.issubdtype(A.dtype, np.complexfloating):
            if OPpart is not None:
                raise ValueError("OPpart should not be specified "
                                 "with sigma=None or complex A")
            mode = 3
        elif OPpart is None or OPpart.lower() == 'r':
            mode = 3
        elif OPpart.lower() == 'i':
            if np.imag(sigma) == 0:
                raise ValueError("OPpart cannot be 'i' if sigma is real")
            mode = 4
        else:
            raise ValueError("OPpart must be one of ('r','i')")

        matvec = _aslinearoperator_with_dtype(A).matvec
        if Minv is not None:
            raise ValueError("Minv should not be specified when sigma is")
        if OPinv is None:
            Minv_matvec = get_OPinv_matvec(A, M, sigma,
                                           symmetric=False, tol=tol)
        else:
            OPinv = _aslinearoperator_with_dtype(OPinv)
            Minv_matvec = OPinv.matvec
        if M is None:
            M_matvec = None
        else:
            M_matvec = _aslinearoperator_with_dtype(M).matvec

    params = _UnsymmetricArpackParams(n, k, A.dtype.char, matvec, mode,
                                      M_matvec, Minv_matvec, sigma,
                                      ncv, v0, maxiter, which, tol)

    with _ARPACK_LOCK:
        while not params.converged:
            params.iterate()

        return params.extract(return_eigenvectors)