def stack(tensors, axis=0, out=None):
    """
    Join a sequence of tensors along a new axis.

    The `axis` parameter specifies the index of the new axis in the dimensions
    of the result. For example, if ``axis=0`` it will be the first dimension
    and if ``axis=-1`` it will be the last dimension.

    Parameters
    ----------
    tensors : sequence of array_like
        Each tensor must have the same shape.
    axis : int, optional
        The axis in the result tensor along which the input tensors are stacked.
    out : Tensor, optional
        If provided, the destination to place the result. The shape must be
        correct, matching that of what stack would have returned if no
        out argument were specified.

    Returns
    -------
    stacked : Tensor
        The stacked tensor has one more dimension than the input tensors.

    See Also
    --------
    concatenate : Join a sequence of tensors along an existing axis.
    split : Split tensor into a list of multiple sub-tensors of equal size.
    block : Assemble tensors from blocks.

    Examples
    --------
    >>> import mars.tensor as mt

    >>> arrays = [mt.random.randn(3, 4) for _ in range(10)]
    >>> mt.stack(arrays, axis=0).shape
    (10, 3, 4)

    >>> mt.stack(arrays, axis=1).shape
    (3, 10, 4)

    >>> mt.stack(arrays, axis=2).shape
    (3, 4, 10)

    >>> a = mt.array([1, 2, 3])
    >>> b = mt.array([2, 3, 4])
    >>> mt.stack((a, b)).execute()
    array([[1, 2, 3],
           [2, 3, 4]])

    >>> mt.stack((a, b), axis=-1).execute()
    array([[1, 2],
           [2, 3],
           [3, 4]])

    """
    tensors = [astensor(t) for t in tensors]

    to_check_shapes = []
    for t in tensors:
        if not any(np.isnan(s) for s in t.shape):
            to_check_shapes.append(t.shape)
    if to_check_shapes and len(set(to_check_shapes)) != 1:
        raise ValueError('all input tensors must have the same shape')

    ndim = len(tensors[0].shape)
    raw_axis = axis
    if axis < 0:
        axis = ndim + axis + 1
    if axis > ndim or axis < 0:
        raise np.AxisError(f'axis {raw_axis} is out of bounds for tensor '
                           f'of dimension {ndim}')

    dtype = np.result_type(*[t.dtype for t in tensors])
    sparse = all(t.issparse() for t in tensors)

    op = TensorStack(axis=axis, dtype=dtype, sparse=sparse)
    return op(tensors, out=out)