def contourf(cube, *args, **kwargs):
    """
    Draws filled contours based on the given Cube.

    Args:

    * coords: list of :class:`~iris.coords.Coord` objects or coordinate names
        Use the given coordinates as the axes for the plot. The order of the
        given coordinates indicates which axis to use for each, where the first
        element is the horizontal axis of the plot and the second element is
        the vertical axis of the plot.

    See :func:`matplotlib.pyplot.contourf` for details of other valid keyword
    arguments.

    """
    coords = kwargs.get('coords')
    kwargs.setdefault('antialiased', True)
    result = _draw_2d_from_points('contourf', None, cube, *args, **kwargs)

    # Matplotlib produces visible seams between anti-aliased polygons.
    # But if the polygons are virtually opaque then we can cover the seams
    # by drawing anti-aliased lines *underneath* the polygon joins.

    # Figure out the alpha level for the contour plot
    if result.alpha is None:
        alpha = result.collections[0].get_facecolor()[0][3]
    else:
        alpha = result.alpha
    # If the contours are anti-aliased and mostly opaque then draw lines under
    # the seams.
    if result.antialiased and alpha > 0.95:
        levels = result.levels
        colors = [c[0] for c in result.tcolors]
        if result.extend == 'neither':
            levels = levels[1:-1]
            colors = colors[:-1]
        elif result.extend == 'min':
            levels = levels[:-1]
            colors = colors[:-1]
        elif result.extend == 'max':
            levels = levels[1:]
            colors = colors[:-1]
        else:
            colors = colors[:-1]
        if len(levels) > 0:
            # Draw the lines just *below* the polygons to ensure we minimise
            # any boundary shift.
            zorder = result.collections[0].zorder - 1
            contour(cube, levels=levels, colors=colors, antialiased=True,
                    zorder=zorder, coords=coords)

    return result