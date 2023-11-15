    def __init__(
        self,
        latitude_of_projection_origin=None,
        longitude_of_central_meridian=None,
        false_easting=None,
        false_northing=None,
        standard_parallels=None,
        ellipsoid=None,
    ):
        """
        Constructs a Albers Conical Equal Area coord system.

        Kwargs:

        * latitude_of_projection_origin:
            True latitude of planar origin in degrees. Defaults to 0.0 .

        * longitude_of_central_meridian:
            True longitude of planar central meridian in degrees.
            Defaults to 0.0 .

        * false_easting:
            X offset from planar origin in metres. Defaults to 0.0 .

        * false_northing:
            Y offset from planar origin in metres. Defaults to 0.0 .

        * standard_parallels (number or iterable of 1 or 2 numbers):
            The one or two latitudes of correct scale.
            Defaults to (20.0, 50.0).

        * ellipsoid (:class:`GeogCS`):
            If given, defines the ellipsoid.

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = _arg_default(
            latitude_of_projection_origin, 0
        )

        #: True longitude of planar central meridian in degrees.
        self.longitude_of_central_meridian = _arg_default(
            longitude_of_central_meridian, 0
        )

        #: X offset from planar origin in metres.
        self.false_easting = _arg_default(false_easting, 0)

        #: Y offset from planar origin in metres.
        self.false_northing = _arg_default(false_northing, 0)

        #: The one or two latitudes of correct scale (tuple of 1 or 2 floats).
        self.standard_parallels = _arg_default(
            standard_parallels, (20, 50), cast_as=_1or2_parallels
        )

        #: Ellipsoid definition (:class:`GeogCS` or None).
        self.ellipsoid = ellipsoid