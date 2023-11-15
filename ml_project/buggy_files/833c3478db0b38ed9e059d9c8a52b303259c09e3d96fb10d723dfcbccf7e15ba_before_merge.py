    def __init__(
        self,
        latitude_of_projection_origin,
        longitude_of_projection_origin,
        false_easting=0.0,
        false_northing=0.0,
        ellipsoid=None,
    ):
        """
        Constructs an Orthographic coord system.

        Args:

        * latitude_of_projection_origin:
            True latitude of planar origin in degrees.

        * longitude_of_projection_origin:
            True longitude of planar origin in degrees.

        Kwargs:

        * false_easting
            X offset from planar origin in metres. Defaults to 0.

        * false_northing
            Y offset from planar origin in metres. Defaults to 0.

        * ellipsoid
            :class:`GeogCS` defining the ellipsoid.

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = float(
            latitude_of_projection_origin
        )

        #: True longitude of planar origin in degrees.
        self.longitude_of_projection_origin = float(
            longitude_of_projection_origin
        )

        #: X offset from planar origin in metres.
        self.false_easting = float(false_easting)

        #: Y offset from planar origin in metres.
        self.false_northing = float(false_northing)

        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid