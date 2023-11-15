def approx_jacobian(x, func, epsilon, *args):
    """
    Approximate the Jacobian matrix of a callable function.

    Parameters
    ----------
    x : array_like
        The state vector at which to compute the Jacobian matrix.
    func : callable f(x,*args)
        The vector-valued function.
    epsilon : float
        The perturbation used to determine the partial derivatives.
    args : sequence
        Additional arguments passed to func.

    Returns
    -------
    An array of dimensions ``(lenf, lenx)`` where ``lenf`` is the length
    of the outputs of `func`, and ``lenx`` is the number of elements in
    `x`.

    Notes
    -----
    The approximation is done using forward differences.

    """
    # approx_derivative returns (m, n) == (lenf, lenx)
    jac = approx_derivative(func, x, method='2-point', abs_step=epsilon,
                            args=args)
    # if func returns a scalar jac.shape will be (lenx,). Make sure
    # it's at least a 2D array.
    return np.atleast_2d(jac)