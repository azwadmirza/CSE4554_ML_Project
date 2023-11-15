def geometry_window(dataset, shapes, pad_x=0, pad_y=0, north_up=True,
                    rotated=False, pixel_precision=3):
    """Calculate the window within the raster that fits the bounds of the
    geometry plus optional padding.  The window is the outermost pixel indices
    that contain the geometry (floor of offsets, ceiling of width and height).

    If shapes do not overlap raster, a WindowError is raised.

    Parameters
    ----------
    dataset: dataset object opened in 'r' mode
        Raster for which the mask will be created.
    shapes: iterable over geometries.
        A geometry is a GeoJSON-like object or implements the geo interface.
        Must be in same coordinate system as dataset.
    pad_x: float
        Amount of padding (as fraction of raster's x pixel size) to add to left
        and right side of bounds.
    pad_y: float
        Amount of padding (as fraction of raster's y pixel size) to add to top
        and bottom of bounds.
    north_up: bool
        If True (default), the origin point of the raster's transform is the
        northernmost point and y pixel values are negative.
    rotated: bool
        If true, some rotation terms exist in the dataset transform (this
        requires special attention.)
    pixel_precision: int
        Number of places of rounding precision for evaluating bounds of shapes.

    Returns
    -------
    window: rasterio.windows.Window instance
    """

    if pad_x:
        pad_x = abs(pad_x * dataset.res[0])

    if pad_y:
        pad_y = abs(pad_y * dataset.res[1])

    if not rotated:
        all_bounds = [bounds(shape, north_up=north_up) for shape in shapes]
        lefts, bottoms, rights, tops = zip(*all_bounds)

        left = min(lefts) - pad_x
        right = max(rights) + pad_x

        if north_up:
            bottom = min(bottoms) - pad_y
            top = max(tops) + pad_y
        else:
            bottom = max(bottoms) + pad_y
            top = min(tops) - pad_y
    else:
        # get the bounds in the pixel domain by specifying a transform to the bounds function
        all_bounds_px = [bounds(shape, transform=~dataset.transform) for shape in shapes]
        # get left, right, top, and bottom as above
        lefts, bottoms, rights, tops = zip(*all_bounds_px)
        left = min(lefts) - pad_x
        right = max(rights) + pad_x
        top = min(tops) - pad_y
        bottom = max(bottoms) + pad_y
        # do some clamping if there are any values less than zero or greater than dataset shape
        left = max(0, left)
        top = max(0, top)
        right = min(dataset.shape[1], right)
        bottom = min(dataset.shape[0], bottom)
        # convert the bounds back to the CRS domain
        left, top = dataset.transform * (left, top)
        right, bottom = dataset.transform * (right, bottom)

    window = dataset.window(left, bottom, right, top)
    window_floored = window.round_offsets(op='floor', pixel_precision=pixel_precision)
    w = math.ceil(window.width + window.col_off - window_floored.col_off)
    h = math.ceil(window.height + window.row_off - window_floored.row_off)
    window = Window(window_floored.col_off, window_floored.row_off, w, h)

    # Make sure that window overlaps raster
    raster_window = Window(0, 0, dataset.width, dataset.height)

    # This will raise a WindowError if windows do not overlap
    window = window.intersection(raster_window)

    return window