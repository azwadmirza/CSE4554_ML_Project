def swapaxes(a, axis1, axis2):
    """
    Interchange two axes of a tensor.

    Parameters
    ----------
    a : array_like
        Input tensor.
    axis1 : int
        First axis.
    axis2 : int
        Second axis.

    Returns
    -------
    a_swapped : Tensor
        If `a` is a Tensor, then a view of `a` is
        returned; otherwise a new tensor is created.

    Examples
    --------
    >>> import mars.tensor as mt

    >>> x = mt.array([[1,2,3]])
    >>> mt.swapaxes(x,0,1).execute()
    array([[1],
           [2],
           [3]])

    >>> x = mt.array([[[0,1],[2,3]],[[4,5],[6,7]]])
    >>> x.execute()
    array([[[0, 1],
            [2, 3]],
           [[4, 5],
            [6, 7]]])

    >>> mt.swapaxes(x,0,2).execute()
    array([[[0, 4],
            [2, 6]],
           [[1, 5],
            [3, 7]]])

    """
    axis1 = validate_axis(a.ndim, axis1)
    axis2 = validate_axis(a.ndim, axis2)

    if axis1 == axis2:
        return a

    op = TensorSwapAxes(axis1, axis2, dtype=a.dtype, sparse=a.issparse())
    return op(a)