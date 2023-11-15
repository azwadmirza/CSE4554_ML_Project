def open_rasterio(filename, chunks=None, cache=None, lock=None):
    """Open a file with rasterio (experimental).

    This should work with any file that rasterio can open (most often:
    geoTIFF). The x and y coordinates are generated automatically from the
    file's geoinformation, shifted to the center of each pixel (see
    `"PixelIsArea" Raster Space
    <http://web.archive.org/web/20160326194152/http://remotesensing.org/geotiff/spec/geotiff2.5.html#2.5.2>`_
    for more information).

    Parameters
    ----------
    filename : str
        Path to the file to open.

    Returns
    -------
    data : DataArray
        The newly created DataArray.
    chunks : int, tuple or dict, optional
        Chunk sizes along each dimension, e.g., ``5``, ``(5, 5)`` or
        ``{'x': 5, 'y': 5}``. If chunks is provided, it used to load the new
        DataArray into a dask array.
    cache : bool, optional
        If True, cache data loaded from the underlying datastore in memory as
        NumPy arrays when accessed to avoid reading from the underlying data-
        store multiple times. Defaults to True unless you specify the `chunks`
        argument to use dask, in which case it defaults to False.
    lock : False, True or threading.Lock, optional
        If chunks is provided, this argument is passed on to
        :py:func:`dask.array.from_array`. By default, a global lock is
        used to avoid issues with concurrent access to the same file when using
        dask's multithreaded backend.
    """

    import rasterio
    riods = rasterio.open(filename, mode='r')

    if cache is None:
        cache = chunks is None

    coords = OrderedDict()

    # Get bands
    if riods.count < 1:
        raise ValueError('Unknown dims')
    coords['band'] = np.asarray(riods.indexes)

    # Get geo coords
    nx, ny = riods.width, riods.height
    dx, dy = riods.res[0], -riods.res[1]
    x0 = riods.bounds.right if dx < 0 else riods.bounds.left
    y0 = riods.bounds.top if dy < 0 else riods.bounds.bottom
    coords['y'] = np.linspace(start=y0 + dy / 2, num=ny,
                              stop=(y0 + (ny - 1) * dy) + dy / 2)
    coords['x'] = np.linspace(start=x0 + dx / 2, num=nx,
                              stop=(x0 + (nx - 1) * dx) + dx / 2)

    # Attributes
    attrs = {}
    if hasattr(riods, 'crs') and riods.crs:
        # CRS is a dict-like object specific to rasterio
        # If CRS is not None, we convert it back to a PROJ4 string using
        # rasterio itself
        attrs['crs'] = riods.crs.to_string()
    if hasattr(riods, 'res'):
        # (width, height) tuple of pixels in units of CRS
        attrs['res'] = riods.res
    if hasattr(riods, 'is_tiled'):
        # Is the TIF tiled? (bool)
        # We cast it to an int for netCDF compatibility
        attrs['is_tiled'] = np.uint8(riods.is_tiled)
    if hasattr(riods, 'transform'):
        # Affine transformation matrix (tuple of floats)
        # Describes coefficients mapping pixel coordinates to CRS
        attrs['transform'] = tuple(riods.transform)
    if hasattr(riods, 'nodatavals'):
        # The nodata values for the raster bands
        attrs['nodatavals'] = tuple([np.nan if nodataval is None else nodataval
                                     for nodataval in riods.nodatavals])

    # Parse extra metadata from tags, if supported
    parsers = {'ENVI': _parse_envi}

    driver = riods.driver
    if driver in parsers:
        meta = parsers[driver](riods.tags(ns=driver))

        for k, v in meta.items():
            # Add values as coordinates if they match the band count,
            # as attributes otherwise
            if isinstance(v, (list, np.ndarray)) and len(v) == riods.count:
                coords[k] = ('band', np.asarray(v))
            else:
                attrs[k] = v

    data = indexing.LazilyIndexedArray(RasterioArrayWrapper(riods))

    # this lets you write arrays loaded with rasterio
    data = indexing.CopyOnWriteArray(data)
    if cache and (chunks is None):
        data = indexing.MemoryCachedArray(data)

    result = DataArray(data=data, dims=('band', 'y', 'x'),
                       coords=coords, attrs=attrs)

    if chunks is not None:
        from dask.base import tokenize
        # augment the token with the file modification time
        try:
            mtime = os.path.getmtime(filename)
        except OSError:
            # the filename is probably an s3 bucket rather than a regular file
            mtime = None
        token = tokenize(filename, mtime, chunks)
        name_prefix = 'open_rasterio-%s' % token
        if lock is None:
            lock = RASTERIO_LOCK
        result = result.chunk(chunks, name_prefix=name_prefix, token=token,
                              lock=lock)

    # Make the file closeable
    result._file_obj = riods

    return result