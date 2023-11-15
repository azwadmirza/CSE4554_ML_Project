def rand(random_state, *dn, **kw):
    """
    Random values in a given shape.

    Create a tensor of the given shape and populate it with
    random samples from a uniform distributionc
    over ``[0, 1)``.

    Parameters
    ----------
    d0, d1, ..., dn : int, optional
        The dimensions of the returned tensor, should all be positive.
        If no argument is given a single Python float is returned.

    Returns
    -------
    out : Tensor, shape ``(d0, d1, ..., dn)``
        Random values.

    See Also
    --------
    random

    Notes
    -----
    This is a convenience function. If you want an interface that
    takes a shape-tuple as the first argument, refer to
    mt.random.random_sample .

    Examples
    --------
    >>> import mars.tensor as mt

    >>> mt.random.rand(3,2).execute()
    array([[ 0.14022471,  0.96360618],  #random
           [ 0.37601032,  0.25528411],  #random
           [ 0.49313049,  0.94909878]]) #random
    """
    if 'dtype' not in kw:
        kw['dtype'] = np.dtype('f8')
    chunks = kw.pop('chunks', None)
    op = TensorRand(state=random_state._state, size=dn, **kw)
    return op(chunks=chunks)