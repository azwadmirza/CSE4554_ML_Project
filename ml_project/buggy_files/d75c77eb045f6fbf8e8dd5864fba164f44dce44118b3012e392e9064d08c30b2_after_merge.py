    def __init__(
        self,
        latitude_of_projection_origin,
        longitude_of_central_meridian,
        false_easting=None,
        false_northing=None,
        scale_factor_at_central_meridian=None,
        ellipsoid=None,
    ):
        """
        Constructs a TransverseMercator object.

        Args:

        * latitude_of_projection_origin:
                True latitude of planar origin in degrees.

        * longitude_of_central_meridian:
                True longitude of planar origin in degrees.

        Kwargs:

        * false_easting:
                X offset from planar origin in metres.
                Defaults to 0.0 .

        * false_northing:
                Y offset from planar origin in metres.
                Defaults to 0.0 .

        * scale_factor_at_central_meridian:
                Reduces the cylinder to slice through the ellipsoid
                (secant form). Used to provide TWO longitudes of zero
                distortion in the area of interest.
                Defaults to 1.0 .

        * ellipsoid (:class:`GeogCS`):
            If given, defines the ellipsoid.

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
        self.false_easting = _arg_default(false_easting, 0)

        #: Y offset from planar origin in metres.
        self.false_northing = _arg_default(false_northing, 0)

        #: Scale factor at the centre longitude.
        self.scale_factor_at_central_meridian = _arg_default(
            scale_factor_at_central_meridian, 1.0
        )

        #: Ellipsoid definition (:class:`GeogCS` or None).
        self.ellipsoid = ellipsoid