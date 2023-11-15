    def __init__(
        self,
        central_lat,
        central_lon,
        false_easting=None,
        false_northing=None,
        true_scale_lat=None,
        ellipsoid=None,
    ):
        """
        Constructs a Stereographic coord system.

        Args:

        * central_lat:
            The latitude of the pole.

        * central_lon:
            The central longitude, which aligns with the y axis.

        Kwargs:

        * false_easting:
            X offset from planar origin in metres. Defaults to 0.0 .

        * false_northing:
            Y offset from planar origin in metres. Defaults to 0.0 .

        * true_scale_lat:
            Latitude of true scale.

        * ellipsoid (:class:`GeogCS`):
            If given, defines the ellipsoid.

        """

        #: True latitude of planar origin in degrees.
        self.central_lat = float(central_lat)

        #: True longitude of planar origin in degrees.
        self.central_lon = float(central_lon)

        #: X offset from planar origin in metres.
        self.false_easting = _arg_default(false_easting, 0)

        #: Y offset from planar origin in metres.
        self.false_northing = _arg_default(false_northing, 0)

        #: Latitude of true scale.
        self.true_scale_lat = _arg_default(
            true_scale_lat, None, cast_as=_float_or_None
        )
        # N.B. the way we use this parameter, we need it to default to None,
        # and *not* to 0.0 .

        #: Ellipsoid definition (:class:`GeogCS` or None).
        self.ellipsoid = ellipsoid