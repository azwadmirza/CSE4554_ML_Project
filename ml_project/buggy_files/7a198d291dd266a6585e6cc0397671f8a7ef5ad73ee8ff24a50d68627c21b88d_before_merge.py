    def __init__(
        self,
        central_lat,
        central_lon,
        false_easting=0.0,
        false_northing=0.0,
        true_scale_lat=None,
        ellipsoid=None,
    ):
        """
        Constructs a Stereographic coord system.

        Args:

            * central_lat
                    The latitude of the pole.

            * central_lon
                    The central longitude, which aligns with the y axis.

        Kwargs:

            * false_easting
                    X offset from planar origin in metres. Defaults to 0.

            * false_northing
                    Y offset from planar origin in metres. Defaults to 0.

            * true_scale_lat
                    Latitude of true scale.

            * ellipsoid
                    :class:`GeogCS` defining the ellipsoid.

        """

        #: True latitude of planar origin in degrees.
        self.central_lat = float(central_lat)

        #: True longitude of planar origin in degrees.
        self.central_lon = float(central_lon)

        #: X offset from planar origin in metres.
        self.false_easting = float(false_easting)

        #: Y offset from planar origin in metres.
        self.false_northing = float(false_northing)

        #: Latitude of true scale.
        self.true_scale_lat = float(true_scale_lat) if true_scale_lat else None

        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid