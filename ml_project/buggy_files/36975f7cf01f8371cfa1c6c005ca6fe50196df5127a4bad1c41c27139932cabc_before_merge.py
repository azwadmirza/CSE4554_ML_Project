def asanyarray(a, dtype=None):
    """
    Convert the input to a masked array, conserving subclasses.

    If `a` is a subclass of `MaskedArray`, its class is conserved.
    No copy is performed if the input is already an `ndarray`.

    Parameters
    ----------
    a : array_like
        Input data, in any form that can be converted to an array.
    dtype : dtype, optional
        By default, the data-type is inferred from the input data.
    order : {'C', 'F'}, optional
        Whether to use row-major ('C') or column-major ('FORTRAN') memory
        representation.  Default is 'C'.

    Returns
    -------
    out : MaskedArray
        MaskedArray interpretation of `a`.

    See Also
    --------
    asarray : Similar to `asanyarray`, but does not conserve subclass.

    Examples
    --------
    >>> x = np.arange(10.).reshape(2, 5)
    >>> x
    array([[ 0.,  1.,  2.,  3.,  4.],
           [ 5.,  6.,  7.,  8.,  9.]])
    >>> np.ma.asanyarray(x)
    masked_array(data =
     [[ 0.  1.  2.  3.  4.]
     [ 5.  6.  7.  8.  9.]],
                 mask =
     False,
           fill_value = 1e+20)
    >>> type(np.ma.asanyarray(x))
    <class 'numpy.ma.core.MaskedArray'>

    """
    return masked_array(a, dtype=dtype, copy=False, keep_mask=True, subok=True)