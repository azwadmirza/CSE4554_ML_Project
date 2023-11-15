    def __init__(
        self,
        semi_major_axis=None,
        semi_minor_axis=None,
        inverse_flattening=None,
        longitude_of_prime_meridian=None,
    ):
        """
        Creates a new GeogCS.

        Kwargs:

        * semi_major_axis, semi_minor_axis:
            Axes of ellipsoid, in metres.  At least one must be given
            (see note below).

        * inverse_flattening:
            Can be omitted if both axes given (see note below).
            Defaults to 0.0 .

        * longitude_of_prime_meridian:
            Specifies the prime meridian on the ellipsoid, in degrees.
            Defaults to 0.0 .

        If just semi_major_axis is set, with no semi_minor_axis or
        inverse_flattening, then a perfect sphere is created from the given
        radius.

        If just two of semi_major_axis, semi_minor_axis, and
        inverse_flattening are given the missing element is calculated from the
        formula:
        :math:`flattening = (major - minor) / major`

        Currently, Iris will not allow over-specification (all three ellipsoid
        parameters).

        Examples::

            cs = GeogCS(6371229)
            pp_cs = GeogCS(iris.fileformats.pp.EARTH_RADIUS)
            airy1830 = GeogCS(semi_major_axis=6377563.396,
                              semi_minor_axis=6356256.909)
            airy1830 = GeogCS(semi_major_axis=6377563.396,
                              inverse_flattening=299.3249646)
            custom_cs = GeogCS(6400000, 6300000)

        """
        # No ellipsoid specified? (0 0 0)
        if (
            (semi_major_axis is None)
            and (semi_minor_axis is None)
            and (inverse_flattening is None)
        ):
            raise ValueError("No ellipsoid specified")

        # Ellipsoid over-specified? (1 1 1)
        if (
            (semi_major_axis is not None)
            and (semi_minor_axis is not None)
            and (inverse_flattening is not None)
        ):
            raise ValueError("Ellipsoid is overspecified")

        # Perfect sphere (semi_major_axis only)? (1 0 0)
        elif semi_major_axis is not None and (
            semi_minor_axis is None and inverse_flattening is None
        ):
            semi_minor_axis = semi_major_axis
            inverse_flattening = 0.0

        # Calculate semi_major_axis? (0 1 1)
        elif semi_major_axis is None and (
            semi_minor_axis is not None and inverse_flattening is not None
        ):
            semi_major_axis = -semi_minor_axis / (
                (1.0 - inverse_flattening) / inverse_flattening
            )

        # Calculate semi_minor_axis? (1 0 1)
        elif semi_minor_axis is None and (
            semi_major_axis is not None and inverse_flattening is not None
        ):
            semi_minor_axis = semi_major_axis - (
                (1.0 / inverse_flattening) * semi_major_axis
            )

        # Calculate inverse_flattening? (1 1 0)
        elif inverse_flattening is None and (
            semi_major_axis is not None and semi_minor_axis is not None
        ):
            if semi_major_axis == semi_minor_axis:
                inverse_flattening = 0.0
            else:
                inverse_flattening = 1.0 / (
                    (semi_major_axis - semi_minor_axis) / semi_major_axis
                )

        # We didn't get enough to specify an ellipse.
        else:
            raise ValueError("Insufficient ellipsoid specification")

        #: Major radius of the ellipsoid in metres.
        self.semi_major_axis = float(semi_major_axis)

        #: Minor radius of the ellipsoid in metres.
        self.semi_minor_axis = float(semi_minor_axis)

        #: :math:`1/f` where :math:`f = (a-b)/a`.
        self.inverse_flattening = float(inverse_flattening)

        #: Describes 'zero' on the ellipsoid in degrees.
        self.longitude_of_prime_meridian = _arg_default(
            longitude_of_prime_meridian, 0
        )