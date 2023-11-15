def bytes(length):
    """Returns random bytes.

    .. note:: This function is just a wrapper for :obj:`numpy.random.bytes`.
        The resulting bytes are generated on the host (NumPy), not GPU.

    .. seealso:: :meth:`numpy.random.bytes
                 <numpy.random.mtrand.RandomState.bytes>`
    """
    # TODO(kmaehashi): should it be provided in CuPy?
    return _numpy.random.bytes(length)