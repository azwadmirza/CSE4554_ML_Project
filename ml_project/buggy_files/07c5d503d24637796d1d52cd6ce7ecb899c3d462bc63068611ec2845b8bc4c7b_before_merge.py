def points(cube, *args, **kwargs):
    """
    Draws sample point positions based on the given Cube.

    Args:

    * coords: list of :class:`~iris.coords.Coord` objects or coordinate names
        Use the given coordinates as the axes for the plot. The order of the
        given coordinates indicates which axis to use for each, where the first
        element is the horizontal axis of the plot and the second element is
        the vertical axis of the plot.

    See :func:`matplotlib.pyplot.scatter` for details of other valid keyword
    arguments.

    """
    _scatter_args = lambda u, v, data, *args, **kwargs: ((u, v) + args, kwargs)
    return _draw_2d_from_points('scatter', _scatter_args, cube,
                                *args, **kwargs)