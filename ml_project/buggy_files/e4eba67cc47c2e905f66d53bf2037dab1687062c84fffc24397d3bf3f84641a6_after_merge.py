    def __init__(
        self,
        latitude_of_projection_origin=None,
        longitude_of_projection_origin=None,
        false_easting=None,
        false_northing=None,
        ellipsoid=None,
    ):
        """
        Constructs a Lambert Azimuthal Equal Area coord system.

        Kwargs:

        * latitude_of_projection_origin:
            True latitude of planar origin in degrees. Defaults to 0.0 .

        * longitude_of_projection_origin:
            True longitude of planar origin in degrees. Defaults to 0.0 .

        * false_easting:
                X offset from planar origin in metres. Defaults to 0.0 .

        * false_northing:
                Y offset from planar origin in metres. Defaults to 0.0 .

        * ellipsoid (:class:`GeogCS`):
            If given, defines the ellipsoid.

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = _arg_default(
            latitude_of_projection_origin, 0
        )

        #: True longitude of planar origin in degrees.
        self.longitude_of_projection_origin = _arg_default(
            longitude_of_projection_origin, 0
        )

        #: X offset from planar origin in metres.
        self.false_easting = _arg_default(false_easting, 0)

        #: Y offset from planar origin in metres.
        self.false_northing = _arg_default(false_northing, 0)

        #: Ellipsoid definition (:class:`GeogCS` or None).
        self.ellipsoid = ellipsoid