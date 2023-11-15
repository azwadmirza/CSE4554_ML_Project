    def __init__(self, path, mode='r', driver=None, schema=None, crs=None,
                 encoding=None, layer=None, vsi=None, archive=None,
                 enabled_drivers=None, crs_wkt=None, **kwargs):

        """The required ``path`` is the absolute or relative path to
        a file, such as '/data/test_uk.shp'. In ``mode`` 'r', data can
        be read only. In ``mode`` 'a', data can be appended to a file.
        In ``mode`` 'w', data overwrites the existing contents of
        a file.

        In ``mode`` 'w', an OGR ``driver`` name and a ``schema`` are
        required. A Proj4 ``crs`` string is recommended. If both ``crs``
        and ``crs_wkt`` keyword arguments are passed, the latter will
        trump the former.

        In 'w' mode, kwargs will be mapped to OGR layer creation
        options.
        """

        if not isinstance(path, string_types):
            raise TypeError("invalid path: %r" % path)
        if not isinstance(mode, string_types) or mode not in ('r', 'w', 'a'):
            raise TypeError("invalid mode: %r" % mode)
        if driver and not isinstance(driver, string_types):
            raise TypeError("invalid driver: %r" % driver)
        if schema and not hasattr(schema, 'get'):
            raise TypeError("invalid schema: %r" % schema)
        if crs and not isinstance(crs, compat.DICT_TYPES + string_types):
            raise TypeError("invalid crs: %r" % crs)
        if crs_wkt and not isinstance(crs_wkt, string_types):
            raise TypeError("invalid crs_wkt: %r" % crs_wkt)
        if encoding and not isinstance(encoding, string_types):
            raise TypeError("invalid encoding: %r" % encoding)
        if layer and not isinstance(layer, tuple(list(string_types) + [int])):
            raise TypeError("invalid name: %r" % layer)
        if vsi:
            if not isinstance(vsi, string_types) or not vfs.valid_vsi(vsi):
                raise TypeError("invalid vsi: %r" % vsi)
        if archive and not isinstance(archive, string_types):
            raise TypeError("invalid archive: %r" % archive)

        # Check GDAL version against drivers
        if (driver == "GPKG" and
                get_gdal_version_num() < calc_gdal_version_num(1, 11, 0)):
            raise DriverError(
                "GPKG driver requires GDAL 1.11.0, fiona was compiled "
                "against: {}".format(get_gdal_release_name()))

        self.session = None
        self.iterator = None
        self._len = 0
        self._bounds = None
        self._driver = None
        self._schema = None
        self._crs = None
        self._crs_wkt = None
        self.env = None
        self.enabled_drivers = enabled_drivers

        self.path = vfs.vsi_path(path, vsi, archive)

        if mode == 'w':
            if layer and not isinstance(layer, string_types):
                raise ValueError("in 'w' mode, layer names must be strings")
            if driver == 'GeoJSON':
                if layer is not None:
                    raise ValueError("the GeoJSON format does not have layers")
                self.name = 'OgrGeoJSON'
            # TODO: raise ValueError as above for other single-layer formats.
            else:
                self.name = layer or os.path.basename(os.path.splitext(path)[0])
        else:
            if layer in (0, None):
                self.name = 0
            else:
                self.name = layer or os.path.basename(os.path.splitext(path)[0])

        self.mode = mode

        if self.mode == 'w':
            if driver == 'Shapefile':
                driver = 'ESRI Shapefile'
            if not driver:
                raise DriverError("no driver")
            elif driver not in supported_drivers:
                raise DriverError(
                    "unsupported driver: %r" % driver)
            elif self.mode not in supported_drivers[driver]:
                raise DriverError(
                    "unsupported mode: %r" % self.mode)
            self._driver = driver

            if not schema:
                raise SchemaError("no schema")
            elif 'properties' not in schema:
                raise SchemaError("schema lacks: properties")
            elif 'geometry' not in schema:
                raise SchemaError("schema lacks: geometry")
            self._schema = schema

            if crs_wkt:
                self._crs_wkt = crs_wkt
            elif crs:
                if 'init' in crs or 'proj' in crs or 'epsg' in crs.lower():
                    self._crs = crs
                else:
                    raise CRSError("crs lacks init or proj parameter")

        if driver_count == 0:
            # create a local manager and enter
            self.env = AWSGDALEnv()
        else:
            self.env = AWSGDALEnv()
        self.env.__enter__()

        self._driver = driver
        kwargs.update(encoding=encoding or '')
        self.encoding = encoding

        try:
            if self.mode == 'r':
                self.session = Session()
                self.session.start(self, **kwargs)
            elif self.mode in ('a', 'w'):
                self.session = WritingSession()
                self.session.start(self, **kwargs)
        except IOError:
            self.session = None
            raise

        if self.session is not None:
            self.guard_driver_mode()
            if not self.encoding:
                self.encoding = self.session.get_fileencoding().lower()