    def __init__(
        self,
        central_lat=None,
        central_lon=None,
        false_easting=None,
        false_northing=None,
        secant_latitudes=None,
        ellipsoid=None,
    ):
        """
        Constructs a LambertConformal coord system.

        Kwargs:

        * central_lat:
                The latitude of "unitary scale".  Defaults to 39.0 .

        * central_lon:
                The central longitude.  Defaults to -96.0 .

        * false_easting:
                X offset from planar origin in metres.  Defaults to 0.0 .

        * false_northing:
                Y offset from planar origin in metres.  Defaults to 0.0 .

        * secant_latitudes (number or iterable of 1 or 2 numbers):
                Latitudes of secant intersection.  One or two.
                Defaults to (33.0, 45.0).

        * ellipsoid (:class:`GeogCS`):
            If given, defines the ellipsoid.

        .. note:

            Default arguments are for the familiar USA map:
            central_lon=-96.0, central_lat=39.0,
            false_easting=0.0, false_northing=0.0,
            secant_latitudes=(33, 45)

        """

        #: True latitude of planar origin in degrees.
        self.central_lat = _arg_default(central_lat, 39.0)

        #: True longitude of planar origin in degrees.
        self.central_lon = _arg_default(central_lon, -96.0)

        #: X offset from planar origin in metres.
        self.false_easting = _arg_default(false_easting, 0)

        #: Y offset from planar origin in metres.
        self.false_northing = _arg_default(false_northing, 0)

        #: The standard parallels of the cone (tuple of 1 or 2 floats).
        self.secant_latitudes = _arg_default(
            secant_latitudes, (33, 45), cast_as=_1or2_parallels
        )

        #: Ellipsoid definition (:class:`GeogCS` or None).
        self.ellipsoid = ellipsoid