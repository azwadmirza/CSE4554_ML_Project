    def __init__(
        self,
        latitude_of_projection_origin=0.0,
        longitude_of_central_meridian=0.0,
        false_easting=0.0,
        false_northing=0.0,
        standard_parallels=(20.0, 50.0),
        ellipsoid=None,
    ):
        """
        Constructs a Albers Conical Equal Area coord system.

        Kwargs:

            * latitude_of_projection_origin
                    True latitude of planar origin in degrees.
                    Defaults to 0.

            * longitude_of_central_meridian
                    True longitude of planar central meridian in degrees.
                    Defaults to 0.

            * false_easting
                    X offset from planar origin in metres. Defaults to 0.

            * false_northing
                    Y offset from planar origin in metres. Defaults to 0.

            * standard_parallels
                    The one or two latitudes of correct scale.
                    Defaults to (20,50).
            * ellipsoid
                    :class:`GeogCS` defining the ellipsoid.

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = latitude_of_projection_origin
        #: True longitude of planar central meridian in degrees.
        self.longitude_of_central_meridian = longitude_of_central_meridian
        #: X offset from planar origin in metres.
        self.false_easting = false_easting
        #: Y offset from planar origin in metres.
        self.false_northing = false_northing
        #: The one or two latitudes of correct scale.
        self.standard_parallels = standard_parallels
        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid