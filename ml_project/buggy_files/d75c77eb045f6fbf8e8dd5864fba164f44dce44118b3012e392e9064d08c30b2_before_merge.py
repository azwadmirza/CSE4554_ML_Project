    def __init__(
        self,
        latitude_of_projection_origin,
        longitude_of_central_meridian,
        false_easting,
        false_northing,
        scale_factor_at_central_meridian,
        ellipsoid=None,
    ):
        """
        Constructs a TransverseMercator object.

        Args:

            * latitude_of_projection_origin
                    True latitude of planar origin in degrees.

            * longitude_of_central_meridian
                    True longitude of planar origin in degrees.

            * false_easting
                    X offset from planar origin in metres.

            * false_northing
                    Y offset from planar origin in metres.

            * scale_factor_at_central_meridian
                    Reduces the cylinder to slice through the ellipsoid
                    (secant form). Used to provide TWO longitudes of zero
                    distortion in the area of interest.

        Kwargs:

            * ellipsoid
                    Optional :class:`GeogCS` defining the ellipsoid.

        Example::

            airy1830 = GeogCS(6377563.396, 6356256.909)
            osgb = TransverseMercator(49, -2, 400000, -100000, 0.9996012717,
                                      ellipsoid=airy1830)

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = float(
            latitude_of_projection_origin
        )

        #: True longitude of planar origin in degrees.
        self.longitude_of_central_meridian = float(
            longitude_of_central_meridian
        )

        #: X offset from planar origin in metres.
        self.false_easting = float(false_easting)

        #: Y offset from planar origin in metres.
        self.false_northing = float(false_northing)

        #: Reduces the cylinder to slice through the ellipsoid (secant form).
        self.scale_factor_at_central_meridian = float(
            scale_factor_at_central_meridian
        )

        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid