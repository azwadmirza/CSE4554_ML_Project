def outline(cube, coords=None):
    """
    Draws cell outlines based on the given Cube.

    Kwargs:

    * coords: list of :class:`~iris.coords.Coord` objects or coordinate names
        Use the given coordinates as the axes for the plot. The order of the
        given coordinates indicates which axis to use for each, where the first
        element is the horizontal axis of the plot and the second element is
        the vertical axis of the plot.

    """
    result = _draw_2d_from_bounds('pcolormesh', cube, facecolors='none',
                                  edgecolors='k', antialiased=True,
                                  coords=coords)
    # set the _is_stroked property to get a single color grid.
    # See https://github.com/matplotlib/matplotlib/issues/1302
    result._is_stroked = False
    if hasattr(result, '_wrapped_collection_fix'):
        result._wrapped_collection_fix._is_stroked = False
    return result