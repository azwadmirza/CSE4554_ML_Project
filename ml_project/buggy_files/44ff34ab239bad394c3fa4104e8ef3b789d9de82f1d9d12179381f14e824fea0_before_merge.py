    def __init__(
        self,
        latitude_of_projection_origin,
        longitude_of_projection_origin,
        perspective_point_height,
        false_easting=0,
        false_northing=0,
        ellipsoid=None,
    ):
        """
        Constructs a Vertical Perspective coord system.

        Args:

        * latitude_of_projection_origin:
            True latitude of planar origin in degrees.

        * longitude_of_projection_origin:
            True longitude of planar origin in degrees.

        * perspective_point_height:
            Altitude of satellite in metres above the surface of the
            ellipsoid.

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

        #: Altitude of satellite in metres.
        # test if perspective_point_height may be cast to float for proj.4
        self.perspective_point_height = float(perspective_point_height)

        #: X offset from planar origin in metres.
        self.false_easting = float(false_easting)

        #: Y offset from planar origin in metres.
        self.false_northing = float(false_northing)

        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid