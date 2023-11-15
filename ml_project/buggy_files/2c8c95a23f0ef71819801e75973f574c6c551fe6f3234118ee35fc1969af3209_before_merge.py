def inv(a):
    """
    Compute the (multiplicative) inverse of a matrix.
    Given a square matrix `a`, return the matrix `ainv` satisfying
    ``dot(a, ainv) = dot(ainv, a) = eye(a.shape[0])``.
    Parameters
    ----------
    a : (..., M, M) array_like
        Matrix to be inverted.
    Returns
    -------
    ainv : (..., M, M) ndarray or matrix
        (Multiplicative) inverse of the matrix `a`.
    Raises
    ------
    LinAlgError
        If `a` is not square or inversion fails.
    Notes
    -----
    .. versionadded:: 1.8.0
    Broadcasting rules apply, see the `numpy.linalg` documentation for
    details.
    Examples
    --------
    >>> import mars.tensor as mt

    >>> a = np.array([[1., 2.], [3., 4.]])
    >>> ainv = mt.linalg.inv(a)
    >>> mt.allclose(mt.dot(a, ainv), mt.eye(2)).execute()
    True
    >>> mt.allclose(mt.dot(ainv, a), mt.eye(2)).execute()
    True
    >>> ainv.execute()
    array([[ -2. ,  1. ],
           [ 1.5, -0.5]])
    """
    # TODO: using some parallel algorithm for matrix inversion.
    from ..datasource import eye

    a = astensor(a)
    return solve(a, eye(a.shape[0], chunk_size=a.params.raw_chunk_size))