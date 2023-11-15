def plotting_extent(source, transform=None):
    """Returns an extent in the format needed
     for matplotlib's imshow (left, right, bottom, top)
     instead of rasterio's bounds (left, bottom, top, right)

    Parameters
    ----------
    source : array or dataset object opened in 'r' mode
        input data
    transform: Affine, required if source is array
        Defines the affine transform if source is an array

    Returns
    -------
    tuple of float
        left, right, bottom, top
    """
    if hasattr(source, 'bounds'):
        extent = (source.bounds.left, source.bounds.right,
                  source.bounds.bottom, source.bounds.top)
    elif not transform:
        raise ValueError(
            "transform is required if source is an array")
    else:
        transform = guard_transform(transform)
        rows, cols = source.shape[0:2]
        left, top = transform * (0, 0)
        right, bottom = transform * (cols, rows)
        extent = (left, right, bottom, top)

    return extent