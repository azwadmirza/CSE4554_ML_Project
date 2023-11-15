def open(
        path,
        mode='r',
        driver=None,
        schema=None,
        crs=None,
        encoding=None,
        layer=None,
        vfs=None,
        enabled_drivers=None,
        crs_wkt=None):
    """Open file at ``path`` in ``mode`` "r" (read), "a" (append), or
    "w" (write) and return a ``Collection`` object.

    In write mode, a driver name such as "ESRI Shapefile" or "GPX" (see
    OGR docs or ``ogr2ogr --help`` on the command line) and a schema
    mapping such as:

      {'geometry': 'Point',
       'properties': [('class', 'int'), ('label', 'str'),
                      ('value', 'float')]}

    must be provided. If a particular ordering of properties ("fields"
    in GIS parlance) in the written file is desired, a list of (key,
    value) pairs as above or an ordered dict is required. If no ordering
    is needed, a standard dict will suffice.

    A coordinate reference system for collections in write mode can be
    defined by the ``crs`` parameter. It takes Proj4 style mappings like

      {'proj': 'longlat', 'ellps': 'WGS84', 'datum': 'WGS84',
       'no_defs': True}

    short hand strings like

      EPSG:4326

    or WKT representations of coordinate reference systems.

    The drivers used by Fiona will try to detect the encoding of data
    files. If they fail, you may provide the proper ``encoding``, such
    as 'Windows-1252' for the Natural Earth datasets.

    When the provided path is to a file containing multiple named layers
    of data, a layer can be singled out by ``layer``.

    A virtual filesystem can be specified. The ``vfs`` parameter may be
    an Apache Commons VFS style string beginning with "zip://" or
    "tar://"". In this case, the ``path`` must be an absolute path
    within that container.

    The drivers enabled for opening datasets may be restricted to those
    listed in the ``enabled_drivers`` parameter. This and the ``driver``
    parameter afford much control over opening of files.

      # Trying only the GeoJSON driver when opening to read, the
      # following raises ``DataIOError``:
      fiona.open('example.shp', driver='GeoJSON')

      # Trying first the GeoJSON driver, then the Shapefile driver,
      # the following succeeds:
      fiona.open(
          'example.shp', enabled_drivers=['GeoJSON', 'ESRI Shapefile'])

    """
    # Parse the vfs into a vsi and an archive path.
    path, vsi, archive = parse_paths(path, vfs)
    if mode in ('a', 'r'):
        if archive:
            if not os.path.exists(archive):
                raise IOError("no such archive file: %r" % archive)
        elif path != '-' and not os.path.exists(path):
            raise IOError("no such file or directory: %r" % path)
        c = Collection(path, mode, driver=driver, encoding=encoding,
                       layer=layer, vsi=vsi, archive=archive,
                       enabled_drivers=enabled_drivers)
    elif mode == 'w':
        if schema:
            # Make an ordered dict of schema properties.
            this_schema = schema.copy()
            this_schema['properties'] = OrderedDict(schema['properties'])
        else:
            this_schema = None
        c = Collection(path, mode, crs=crs, driver=driver, schema=this_schema,
                       encoding=encoding, layer=layer, vsi=vsi, archive=archive,
                       enabled_drivers=enabled_drivers, crs_wkt=crs_wkt)
    else:
        raise ValueError(
            "mode string must be one of 'r', 'w', or 'a', not %s" % mode)
    return c