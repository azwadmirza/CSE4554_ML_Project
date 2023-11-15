    def __init__(
        self,
        longitude_of_projection_origin=None,
        ellipsoid=None,
        standard_parallel=None,
    ):
        """
        Constructs a Mercator coord system.

        Kwargs:

        * longitude_of_projection_origin:
            True longitude of planar origin in degrees. Defaults to 0.0 .

        * ellipsoid (:class:`GeogCS`):
            If given, defines the ellipsoid.

        * standard_parallel:
            The latitude where the scale is 1. Defaults to 0.0 .

        """
        #: True longitude of planar origin in degrees.
        self.longitude_of_projection_origin = _arg_default(
            longitude_of_projection_origin, 0
        )

        #: Ellipsoid definition (:class:`GeogCS` or None).
        self.ellipsoid = ellipsoid

        #: The latitude where the scale is 1.
        self.standard_parallel = _arg_default(standard_parallel, 0)