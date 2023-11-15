def plot(cube, *args, **kwargs):
    """
    Draws a line plot based on the given Cube.

    Args:

    * coords: list of :class:`~iris.coords.Coord` objects or coordinate names
        Use the given coordinates as the axes for the plot. The order of the
        given coordinates indicates which axis to use for each, where the first
        element is the horizontal axis of the plot and the second element is
        the vertical axis of the plot.

    See :func:`matplotlib.pyplot.plot` for details of other valid keyword
    arguments.

    """
    _plot_args = None
    return _draw_1d_from_points('plot', _plot_args, cube, *args, **kwargs)