    def points(self, points):
        """Points must be set along each axial direction.

        Please set the point coordinates with the ``x``, ``y``, and ``z``
        setters.

        This setter overrides the base class's setter to ensure a user does not
        attempt to set them.

        """
        raise AttributeError("The points cannot be set. The points of "
            "`RectilinearGrid` are defined in each axial direction. Please "
            "use the `x`, `y`, and `z` setters individually."
            )