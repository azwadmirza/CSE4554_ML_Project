    def __init__(self, shell=None, holes=None):
        """
        Parameters
        ----------
        shell : sequence
            A sequence of (x, y [,z]) numeric coordinate pairs or triples.
            Also can be a sequence of Point objects.
        holes : sequence
            A sequence of objects which satisfy the same requirements as the
            shell parameters above

        Example
        -------
        Create a square polygon with no holes

          >>> coords = ((0., 0.), (0., 1.), (1., 1.), (1., 0.), (0., 0.))
          >>> polygon = Polygon(coords)
          >>> polygon.area
          1.0
        """
        BaseGeometry.__init__(self)

        if shell is not None:
            ret = geos_polygon_from_py(shell, holes)
            if ret is not None:
                self._geom, self._ndim = ret
            else:
                self.empty()