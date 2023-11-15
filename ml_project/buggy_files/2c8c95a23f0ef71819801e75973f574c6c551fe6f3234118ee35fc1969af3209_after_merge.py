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
    a = astensor(a)
    if a.ndim != 2:
        raise LinAlgError('{0}-dimensional array given. '
                          'Tensor must be two-dimensional'.format(a.ndim))
    if a.shape[0] != a.shape[1]:
        raise LinAlgError('Input must be square')

    tiny_inv = np.linalg.inv(np.array([[1, 2], [2, 5]], dtype=a.dtype))
    op = TensorInv(dtype=tiny_inv.dtype, sparse=a.is_sparse())
    return op(a)