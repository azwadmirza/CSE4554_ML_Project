def reproject(
        source,
        destination,
        src_transform=None,
        src_crs=None,
        src_nodata=None,
        dst_transform=None,
        dst_crs=None,
        dst_nodata=None,
        resampling=Resampling.nearest,
        **kwargs):
    """
    Reproject a source raster to a destination raster.

    If the source and destination are ndarrays, coordinate reference
    system definitions and affine transformation parameters are required
    for reprojection.

    If the source and destination are rasterio Bands, shorthand for
    bands of datasets on disk, the coordinate reference systems and
    transforms will be read from the appropriate datasets.

    Parameters
    ------------
    source: ndarray or rasterio Band
        Source raster.
    destination: ndarray or rasterio Band
        Target raster.
    src_transform: affine transform object, optional
        Source affine transformation.  Required if source and destination
        are ndarrays.  Will be derived from source if it is a rasterio Band.
    src_crs: dict, optional
        Source coordinate reference system, in rasterio dict format.
        Required if source and destination are ndarrays.
        Will be derived from source if it is a rasterio Band.
        Example: {'init': 'EPSG:4326'}
    src_nodata: int or float, optional
        The source nodata value.  Pixels with this value will not be used
        for interpolation.  If not set, it will be default to the
        nodata value of the source image if a masked ndarray or rasterio band,
        if available.  Must be provided if dst_nodata is not None.
    dst_transform: affine transform object, optional
        Target affine transformation.  Required if source and destination
        are ndarrays.  Will be derived from target if it is a rasterio Band.
    dst_crs: dict, optional
        Target coordinate reference system.  Required if source and destination
        are ndarrays.  Will be derived from target if it is a rasterio Band.
    dst_nodata: int or float, optional
        The nodata value used to initialize the destination; it will remain
        in all areas not covered by the reprojected source.  Defaults to the
        nodata value of the destination image (if set), the value of
        src_nodata, or 0 (GDAL default).
    resampling: int
        Resampling method to use.  One of the following:
            Resampling.nearest,
            Resampling.bilinear,
            Resampling.cubic,
            Resampling.cubic_spline,
            Resampling.lanczos,
            Resampling.average,
            Resampling.mode
    kwargs:  dict, optional
        Additional arguments passed to transformation function.

    Returns
    ---------
    out: None
        Output is written to destination.
    """
    # Resampling guard.
    try:
        Resampling(resampling)
        if resampling == 7:
            raise ValueError
    except ValueError:
        raise ValueError(
            "resampling must be one of: {0}".format(", ".join(
                ['Resampling.{0}'.format(k) for k in
                 Resampling.__members__.keys() if k != 'gauss'])))

    # If working with identity transform, assume it is crs-less data
    # and that translating the matrix very slightly will avoid #674
    eps = 1e-100
    if src_transform and guard_transform(src_transform).is_identity:
        src_transform = src_transform.translation(eps, eps)
    if dst_transform and guard_transform(dst_transform).is_identity:
        dst_transform = dst_transform.translation(eps, eps)

    if src_transform:
        src_transform = guard_transform(src_transform).to_gdal()
    if dst_transform:
        dst_transform = guard_transform(dst_transform).to_gdal()

    # Passing None can cause segfault, use empty dict
    if src_crs is None:
        src_crs = {}
    if dst_crs is None:
        dst_crs = {}

    _reproject(
        source,
        destination,
        src_transform,
        src_crs,
        src_nodata,
        dst_transform,
        dst_crs,
        dst_nodata,
        resampling,
        **kwargs)