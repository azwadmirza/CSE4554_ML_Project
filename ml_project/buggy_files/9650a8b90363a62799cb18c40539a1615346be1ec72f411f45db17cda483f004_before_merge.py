def raster_geometry_mask(dataset, shapes, all_touched=False, invert=False,
                         crop=False, pad=False, pad_width=0.5):
    """Create a mask from shapes, transform, and optional window within original
    raster.

    By default, mask is intended for use as a numpy mask, where pixels that
    overlap shapes are False.

    If shapes do not overlap the raster and crop=True, a ValueError is
    raised.  Otherwise, a warning is raised, and a completely True mask
    is returned (if invert is False).

    Parameters
    ----------
    dataset : a dataset object opened in 'r' mode
        Raster for which the mask will be created.
    shapes : iterable object
        The values must be a GeoJSON-like dict or an object that implements
        the Python geo interface protocol (such as a Shapely Polygon).
    all_touched : bool (opt)
        Include a pixel in the mask if it touches any of the shapes.
        If False (default), include a pixel only if its center is within one of
        the shapes, or if it is selected by Bresenham's line algorithm.
    invert : bool (opt)
        If False (default), mask will be `False` inside shapes and `True`
        outside.  If True, mask will be `True` inside shapes and `False`
        outside.
    crop : bool (opt)
        Whether to crop the dataset to the extent of the shapes. Defaults to
        False.
    pad : bool (opt)
        If True, the features will be padded in each direction by
        one half of a pixel prior to cropping dataset. Defaults to False.
    pad_width : float (opt)
        If pad is set (to maintain back-compatibility), then this will be the
        pixel-size width of the padding around the mask.

    Returns
    -------
    tuple

        Three elements:

            mask : numpy ndarray of type 'bool'
                Mask that is `True` outside shapes, and `False` within shapes.

            out_transform : affine.Affine()
                Information for mapping pixel coordinates in `masked` to another
                coordinate system.

            window: rasterio.windows.Window instance
                Window within original raster covered by shapes.  None if crop
                is False.
    """
    if crop and invert:
        raise ValueError("crop and invert cannot both be True.")

    if crop and pad:
        pad_x = pad_width
        pad_y = pad_width
    else:
        pad_x = 0
        pad_y = 0

    north_up = dataset.transform.e <= 0
    rotated = dataset.transform.b != 0 or dataset.transform.d != 0

    try:
        window = geometry_window(dataset, shapes, north_up=north_up, rotated=rotated,
                                 pad_x=pad_x, pad_y=pad_y)

    except WindowError:
        # If shapes do not overlap raster, raise Exception or UserWarning
        # depending on value of crop
        if crop:
            raise ValueError('Input shapes do not overlap raster.')
        else:
            warnings.warn('shapes are outside bounds of raster. '
                          'Are they in different coordinate reference systems?')

        # Return an entirely True mask (if invert is False)
        mask = np.ones(shape=dataset.shape[-2:], dtype='bool') * (not invert)
        return mask, dataset.transform, None

    if crop:
        transform = dataset.window_transform(window)
        out_shape = (int(window.height), int(window.width))

    else:
        window = None
        transform = dataset.transform
        out_shape = (int(dataset.height), int(dataset.width))

    mask = geometry_mask(shapes, transform=transform, invert=invert,
                         out_shape=out_shape, all_touched=all_touched)

    return mask, transform, window