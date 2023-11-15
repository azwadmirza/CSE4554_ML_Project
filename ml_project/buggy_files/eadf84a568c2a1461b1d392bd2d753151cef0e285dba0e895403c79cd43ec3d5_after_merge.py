def _infer_xy_labels_3d(darray, x, y, rgb):
    """
    Determine x and y labels for showing RGB images.

    Attempts to infer which dimension is RGB/RGBA by size and order of dims.

    """
    assert rgb is None or rgb != x
    assert rgb is None or rgb != y
    # Start by detecting and reporting invalid combinations of arguments
    assert darray.ndim == 3
    not_none = [a for a in (x, y, rgb) if a is not None]
    if len(set(not_none)) < len(not_none):
        raise ValueError(
            'Dimension names must be None or unique strings, but imshow was '
            'passed x=%r, y=%r, and rgb=%r.' % (x, y, rgb))
    for label in not_none:
        if label not in darray.dims:
            raise ValueError('%r is not a dimension' % (label,))

    # Then calculate rgb dimension if certain and check validity
    could_be_color = [label for label in darray.dims
                      if darray[label].size in (3, 4) and label not in (x, y)]
    if rgb is None and not could_be_color:
        raise ValueError(
            'A 3-dimensional array was passed to imshow(), but there is no '
            'dimension that could be color.  At least one dimension must be '
            'of size 3 (RGB) or 4 (RGBA), and not given as x or y.')
    if rgb is None and len(could_be_color) == 1:
        rgb = could_be_color[0]
    if rgb is not None and darray[rgb].size not in (3, 4):
        raise ValueError('Cannot interpret dim %r of size %s as RGB or RGBA.'
                         % (rgb, darray[rgb].size))

    # If rgb dimension is still unknown, there must be two or three dimensions
    # in could_be_color.  We therefore warn, and use a heuristic to break ties.
    if rgb is None:
        assert len(could_be_color) in (2, 3)
        rgb = could_be_color[-1]
        warnings.warn(
            'Several dimensions of this array could be colors.  Xarray '
            'will use the last possible dimension (%r) to match '
            'matplotlib.pyplot.imshow.  You can pass names of x, y, '
            'and/or rgb dimensions to override this guess.' % rgb)
    assert rgb is not None

    # Finally, we pick out the red slice and delegate to the 2D version:
    return _infer_xy_labels(darray.isel(**{rgb: 0}), x, y)