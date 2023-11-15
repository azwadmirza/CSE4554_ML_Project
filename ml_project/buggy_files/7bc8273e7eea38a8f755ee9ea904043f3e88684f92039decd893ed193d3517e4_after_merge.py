def _cholesky(a, lower=False, overwrite_a=False, clean=True,
              check_finite=True):
    """Common code for cholesky() and cho_factor()."""

    a1 = asarray_chkfinite(a) if check_finite else asarray(a)
    a1 = atleast_2d(a1)

    # Dimension check
    if a1.ndim != 2:
        raise ValueError('Input array needs to be 2 dimensional but received '
                         'a {}d-array.'.format(a1.ndim))
    # Squareness check
    if a1.shape[0] != a1.shape[1]:
        raise ValueError('Input array is expected to be square but has '
                         'the shape: {}.'.format(a1.shape))

    # Quick return for square empty array
    if a1.size == 0:
        return a1.copy(), lower

    overwrite_a = overwrite_a or _datacopied(a1, a)
    potrf, = get_lapack_funcs(('potrf',), (a1,))
    c, info = potrf(a1, lower=lower, overwrite_a=overwrite_a, clean=clean)
    if info > 0:
        raise LinAlgError("%d-th leading minor of the array is not positive "
                          "definite" % info)
    if info < 0:
        raise ValueError('LAPACK reported an illegal value in {}-th argument'
                         'on entry to "POTRF".'.format(-info))
    return c, lower