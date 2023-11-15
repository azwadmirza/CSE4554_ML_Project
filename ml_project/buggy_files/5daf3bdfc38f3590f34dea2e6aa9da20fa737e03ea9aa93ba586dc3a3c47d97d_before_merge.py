    def __init__(
        self,
        grid_north_pole_latitude,
        grid_north_pole_longitude,
        north_pole_grid_longitude=0,
        ellipsoid=None,
    ):
        """
        Constructs a coordinate system with rotated pole, on an
        optional :class:`GeogCS`.

        Args:

            * grid_north_pole_latitude  - The true latitude of the rotated
                                          pole in degrees.
            * grid_north_pole_longitude - The true longitude of the rotated
                                          pole in degrees.

        Kwargs:

            * north_pole_grid_longitude - Longitude of true north pole in
                                          rotated grid in degrees. Default = 0.
            * ellipsoid                 - Optional :class:`GeogCS` defining
                                          the ellipsoid.

        Examples::

            rotated_cs = RotatedGeogCS(30, 30)
            another_cs = RotatedGeogCS(30, 30,
                                       ellipsoid=GeogCS(6400000, 6300000))

        """
        #: The true latitude of the rotated pole in degrees.
        self.grid_north_pole_latitude = float(grid_north_pole_latitude)

        #: The true longitude of the rotated pole in degrees.
        self.grid_north_pole_longitude = float(grid_north_pole_longitude)

        #: Longitude of true north pole in rotated grid in degrees.
        self.north_pole_grid_longitude = float(north_pole_grid_longitude)

        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid