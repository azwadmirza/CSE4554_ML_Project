def geometry_window(
    dataset,
    shapes,
    pad_x=0,
    pad_y=0,
    north_up=None,
    rotated=None,
    pixel_precision=None,
    boundless=False,
):
    """Calculate the window within the raster that fits the bounds of
    the geometry plus optional padding.  The window is the outermost
    pixel indices that contain the geometry (floor of offsets, ceiling
    of width and height).

    If shapes do not overlap raster, a WindowError is raised.

    Parameters
    ----------
    dataset : dataset object opened in 'r' mode
        Raster for which the mask will be created.
    shapes : iterable over geometries.
        A geometry is a GeoJSON-like object or implements the geo
        interface.  Must be in same coordinate system as dataset.
    pad_x : float
        Amount of padding (as fraction of raster's x pixel size) to add
        to left and right side of bounds.
    pad_y : float
        Amount of padding (as fraction of raster's y pixel size) to add
        to top and bottom of bounds.
    north_up : optional
        This parameter is ignored since version 1.2.1. A deprecation
        warning will be emitted in 1.3.0.
    rotated : optional
        This parameter is ignored since version 1.2.1. A deprecation
        warning will be emitted in 1.3.0.
    pixel_precision : int or float, optional
        Number of places of rounding precision or absolute precision for
        evaluating bounds of shapes.
    boundless : bool, optional
        Whether to allow a boundless window or not.

    Returns
    -------
    rasterio.windows.Window

    """

    if pad_x:
        pad_x = abs(pad_x * dataset.res[0])

    if pad_y:
        pad_y = abs(pad_y * dataset.res[1])

    all_bounds = [bounds(shape) for shape in shapes]

    xs = [
        x
        for (left, bottom, right, top) in all_bounds
        for x in (left - pad_x, right + pad_x, right + pad_x, left - pad_x)
    ]
    ys = [
        y
        for (left, bottom, right, top) in all_bounds
        for y in (top + pad_y, top + pad_y, bottom - pad_x, bottom - pad_x)
    ]

    rows1, cols1 = rowcol(
        dataset.transform, xs, ys, op=math.floor, precision=pixel_precision
    )

    if isinstance(rows1, (int, float)):
        rows1 = [rows1]
    if isinstance(cols1, (int, float)):
        cols1 = [cols1]

    rows2, cols2 = rowcol(
        dataset.transform, xs, ys, op=math.ceil, precision=pixel_precision
    )

    if isinstance(rows2, (int, float)):
        rows2 = [rows2]
    if isinstance(cols2, (int, float)):
        cols2 = [cols2]

    rows = rows1 + rows2
    cols = cols1 + cols2

    row_start, row_stop = min(rows), max(rows)
    col_start, col_stop = min(cols), max(cols)

    window = Window(
        col_off=col_start,
        row_off=row_start,
        width=max(col_stop - col_start, 0.0),
        height=max(row_stop - row_start, 0.0),
    )

    # Make sure that window overlaps raster
    raster_window = Window(0, 0, dataset.width, dataset.height)
    if not boundless:
        window = window.intersection(raster_window)

    return window