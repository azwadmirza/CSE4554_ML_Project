    def points(self, points):
        """Points cannot be set.

        This setter overrides the base class's setter to ensure a user does not
        attempt to set them. See https://github.com/pyvista/pyvista/issues/713.

        """
        raise AttributeError("The points cannot be set. The points of "
            "`UniformGrid`/`vtkImageData` are implicitly defined by the "
            "`origin`, `spacing`, and `dimensions` of the grid."
            )