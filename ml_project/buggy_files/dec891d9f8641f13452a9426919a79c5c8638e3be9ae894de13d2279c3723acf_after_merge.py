def flatnonzero(a):
    """Return indices that are non-zero in the flattened version of a.

    This is equivalent to a.ravel().nonzero()[0].

    Args:
        a (cupy.ndarray): input array

    Returns:
        cupy.ndarray: Output array,
        containing the indices of the elements of a.ravel() that are non-zero.

    .. seealso:: :func:`numpy.flatnonzero`
    """
    assert isinstance(a, core.ndarray)
    return a.ravel().nonzero()[0]