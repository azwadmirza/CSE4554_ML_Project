    def __init__(
        self,
        latitude_of_projection_origin=0.0,
        longitude_of_projection_origin=0.0,
        false_easting=0.0,
        false_northing=0.0,
        ellipsoid=None,
    ):
        """
        Constructs a Lambert Azimuthal Equal Area coord system.

        Kwargs:

            * latitude_of_projection_origin
                    True latitude of planar origin in degrees. Defaults to 0.

            * longitude_of_projection_origin
                    True longitude of planar origin in degrees. Defaults to 0.

            * false_easting
                    X offset from planar origin in metres. Defaults to 0.

            * false_northing
                    Y offset from planar origin in metres. Defaults to 0.

            * ellipsoid
                    :class:`GeogCS` defining the ellipsoid.

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = latitude_of_projection_origin
        #: True longitude of planar origin in degrees.
        self.longitude_of_projection_origin = longitude_of_projection_origin
        #: X offset from planar origin in metres.
        self.false_easting = false_easting
        #: Y offset from planar origin in metres.
        self.false_northing = false_northing
        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid