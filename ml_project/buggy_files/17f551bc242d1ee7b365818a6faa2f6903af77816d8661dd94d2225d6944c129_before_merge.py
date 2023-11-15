    def __init__(
        self,
        longitude_of_projection_origin=0.0,
        ellipsoid=None,
        standard_parallel=0.0,
    ):
        """
        Constructs a Mercator coord system.

        Kwargs:
            * longitude_of_projection_origin
                    True longitude of planar origin in degrees.
            * ellipsoid
                    :class:`GeogCS` defining the ellipsoid.
            * standard_parallel
                    the latitude where the scale is 1. Defaults to 0 degrees.

        """
        #: True longitude of planar origin in degrees.
        self.longitude_of_projection_origin = longitude_of_projection_origin
        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid
        #: The latitude where the scale is 1 (defaults to 0 degrees).
        self.standard_parallel = standard_parallel