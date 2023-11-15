    def __init__(
        self,
        central_lat=39.0,
        central_lon=-96.0,
        false_easting=0.0,
        false_northing=0.0,
        secant_latitudes=(33, 45),
        ellipsoid=None,
    ):
        """
        Constructs a LambertConformal coord system.

        Kwargs:

            * central_lat
                    The latitude of "unitary scale".

            * central_lon
                    The central longitude.

            * false_easting
                    X offset from planar origin in metres.

            * false_northing
                    Y offset from planar origin in metres.

            * secant_latitudes
                    Latitudes of secant intersection.

            * ellipsoid
                    :class:`GeogCS` defining the ellipsoid.

        .. note:

            Default arguments are for the familiar USA map:
            central_lon=-96.0, central_lat=39.0,
            false_easting=0.0, false_northing=0.0,
            secant_latitudes=(33, 45)

        """

        #: True latitude of planar origin in degrees.
        self.central_lat = central_lat
        #: True longitude of planar origin in degrees.
        self.central_lon = central_lon
        #: X offset from planar origin in metres.
        self.false_easting = false_easting
        #: Y offset from planar origin in metres.
        self.false_northing = false_northing
        #: The one or two standard parallels of the cone.
        try:
            self.secant_latitudes = tuple(secant_latitudes)
        except TypeError:
            self.secant_latitudes = (secant_latitudes,)
        nlats = len(self.secant_latitudes)
        if nlats == 0 or nlats > 2:
            emsg = "Either one or two secant latitudes required, got {}"
            raise ValueError(emsg.format(nlats))
        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid