def matrix_power(M, n):
    """
    Raise a square matrix to the (integer) power `n`.

    For positive integers `n`, the power is computed by repeated matrix
    squarings and matrix multiplications. If ``n == 0``, the identity matrix
    of the same shape as M is returned. If ``n < 0``, the inverse
    is computed and then raised to the ``abs(n)``.

    Parameters
    ----------
    M : ndarray or matrix object
        Matrix to be "powered."  Must be square, i.e. ``M.shape == (m, m)``,
        with `m` a positive integer.
    n : int
        The exponent can be any integer or long integer, positive,
        negative, or zero.

    Returns
    -------
    M**n : ndarray or matrix object
        The return value is the same shape and type as `M`;
        if the exponent is positive or zero then the type of the
        elements is the same as those of `M`. If the exponent is
        negative the elements are floating-point.

    Raises
    ------
    LinAlgError
        If the matrix is not numerically invertible.

    See Also
    --------
    matrix
        Provides an equivalent function as the exponentiation operator
        (``**``, not ``^``).

    Examples
    --------
    >>> from numpy import linalg as LA
    >>> i = np.array([[0, 1], [-1, 0]]) # matrix equiv. of the imaginary unit
    >>> LA.matrix_power(i, 3) # should = -i
    array([[ 0, -1],
           [ 1,  0]])
    >>> LA.matrix_power(np.matrix(i), 3) # matrix arg returns matrix
    matrix([[ 0, -1],
            [ 1,  0]])
    >>> LA.matrix_power(i, 0)
    array([[1, 0],
           [0, 1]])
    >>> LA.matrix_power(i, -3) # should = 1/(-i) = i, but w/ f.p. elements
    array([[ 0.,  1.],
           [-1.,  0.]])

    Somewhat more sophisticated example

    >>> q = np.zeros((4, 4))
    >>> q[0:2, 0:2] = -i
    >>> q[2:4, 2:4] = i
    >>> q # one of the three quaternion units not equal to 1
    array([[ 0., -1.,  0.,  0.],
           [ 1.,  0.,  0.,  0.],
           [ 0.,  0.,  0.,  1.],
           [ 0.,  0., -1.,  0.]])
    >>> LA.matrix_power(q, 2) # = -np.eye(4)
    array([[-1.,  0.,  0.,  0.],
           [ 0., -1.,  0.,  0.],
           [ 0.,  0., -1.,  0.],
           [ 0.,  0.,  0., -1.]])

    """
    M = asanyarray(M)
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("input must be a square array")
    if not issubdtype(type(n), N.integer):
        raise TypeError("exponent must be an integer")

    from numpy.linalg import inv

    if n==0:
        M = M.copy()
        M[:] = identity(M.shape[0])
        return M
    elif n<0:
        M = inv(M)
        n *= -1

    result = M
    if n <= 3:
        for _ in range(n-1):
            result=N.dot(result, M)
        return result

    # binary decomposition to reduce the number of Matrix
    # multiplications for n > 3.
    beta = binary_repr(n)
    Z, q, t = M, 0, len(beta)
    while beta[t-q-1] == '0':
        Z = N.dot(Z, Z)
        q += 1
    result = Z
    for k in range(q+1, t):
        Z = N.dot(Z, Z)
        if beta[t-k-1] == '1':
            result = N.dot(result, Z)
    return result