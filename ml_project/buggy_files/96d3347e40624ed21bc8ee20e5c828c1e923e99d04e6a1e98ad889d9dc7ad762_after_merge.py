def contour(cube, *args, **kwargs):
    """
    Draws contour lines based on the given Cube.

    Kwargs:

    * coords: list of :class:`~iris.coords.Coord` objects or coordinate names
        Use the given coordinates as the axes for the plot. The order of the
        given coordinates indicates which axis to use for each, where the first
        element is the horizontal axis of the plot and the second element is
        the vertical axis of the plot.

    See :func:`matplotlib.pyplot.contour` for details of other valid keyword
    arguments.

    """
    result = _draw_2d_from_points('contour', None, cube, *args, **kwargs)
    return result