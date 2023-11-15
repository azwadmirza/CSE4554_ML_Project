def from_bounds(
    left, bottom, right, top, transform=None, height=None, width=None, precision=None
):
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

    rows, cols = rowcol(
        transform,
        [left, right, right, left],
        [top, top, bottom, bottom],
        op=float,
        precision=precision,
    )
    row_start, row_stop = min(rows), max(rows)
    col_start, col_stop = min(cols), max(cols)

    return Window(
        col_off=col_start,
        row_off=row_start,
        width=max(col_stop - col_start, 0.0),
        height=max(row_stop - row_start, 0.0),
    )