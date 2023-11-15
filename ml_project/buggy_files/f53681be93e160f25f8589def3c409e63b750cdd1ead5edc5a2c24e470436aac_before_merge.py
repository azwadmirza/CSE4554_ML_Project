def from_bounds(left, bottom, right, top, transform=None,
                height=None, width=None, precision=None):
    """Get the window corresponding to the bounding coordinates.

    Parameters
    ----------
    left: float, required
        Left (west) bounding coordinates
    bottom: float, required
        Bottom (south) bounding coordinates
    right: float, required
        Right (east) bounding coordinates
    top: float, required
        Top (north) bounding coordinates
    transform: Affine, required
        Affine transform matrix.
    height: int, required
        Number of rows of the window.
    width: int, required
        Number of columns of the window.
    precision: int or float, optional
        An integer number of decimal points of precision when computing
        inverse transform, or an absolute float precision.

    Returns
    -------
    Window
        A new Window.

    Raises
    ------
    WindowError
        If a window can't be calculated.

    """
    if not isinstance(transform, Affine):  # TODO: RPCs?
        raise WindowError("A transform object is required to calculate the window")

    row_start, col_start = rowcol(
        transform, left, top, op=float, precision=precision)

    row_stop, col_stop = rowcol(
        transform, right, bottom, op=float, precision=precision)

    return Window.from_slices(
        (row_start, row_stop), (col_start, col_stop), height=height,
        width=width, boundless=True)