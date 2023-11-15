    def __init__(
        self,
        latitude_of_projection_origin,
        longitude_of_projection_origin,
        perspective_point_height,
        sweep_angle_axis,
        false_easting=None,
        false_northing=None,
        ellipsoid=None,
    ):

        """
        Constructs a Geostationary coord system.

        Args:

        * latitude_of_projection_origin (float):
            True latitude of planar origin in degrees.

        * longitude_of_projection_origin (float):
            True longitude of planar origin in degrees.

        * perspective_point_height (float):
            Altitude of satellite in metres above the surface of the ellipsoid.

        * sweep_angle_axis (string):
            The axis along which the satellite instrument sweeps - 'x' or 'y'.

        Kwargs:

        * false_easting (float):
            X offset from planar origin in metres. Defaults to 0.

        * false_northing (float):
            Y offset from planar origin in metres. Defaults to 0.

        * ellipsoid (iris.coord_systems.GeogCS):
            :class:`GeogCS` defining the ellipsoid.

        """
        #: True latitude of planar origin in degrees.
        self.latitude_of_projection_origin = float(
            latitude_of_projection_origin
        )
        if self.latitude_of_projection_origin != 0.0:
            raise ValueError(
                "Non-zero latitude of projection currently not"
                " supported by Cartopy."
            )

        #: True longitude of planar origin in degrees.
        self.longitude_of_projection_origin = float(
            longitude_of_projection_origin
        )

        #: Altitude of satellite in metres.
        # test if perspective_point_height may be cast to float for proj.4
        self.perspective_point_height = float(perspective_point_height)

        #: X offset from planar origin in metres.
        if false_easting is None:
            false_easting = 0
        self.false_easting = float(false_easting)

        #: Y offset from planar origin in metres.
        if false_northing is None:
            false_northing = 0
        self.false_northing = float(false_northing)

        #: The axis along which the satellite instrument sweeps - 'x' or 'y'.
        self.sweep_angle_axis = sweep_angle_axis
        if self.sweep_angle_axis not in ("x", "y"):
            raise ValueError('Invalid sweep_angle_axis - must be "x" or "y"')

        #: Ellipsoid definition.
        self.ellipsoid = ellipsoid