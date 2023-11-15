def _map_common(draw_method_name, arg_func, mode, cube, data, *args, **kwargs):
    """
    Draw the given cube on a map using its points or bounds.

    "Mode" parameter will switch functionality between POINT or BOUND plotting.

    """
    # get the 2d x and 2d y from the CS
    if mode == iris.coords.POINT_MODE:
        x, y = cartography.get_xy_grids(cube)
    else:
        try:
            x, y = cartography.get_xy_contiguous_bounded_grids(cube)
        # Exception translation.
        except iris.exceptions.CoordinateMultiDimError:
            raise ValueError("Could not get XY grid from bounds. "
                             "X or Y coordinate not 1D.")
        except ValueError:
            raise ValueError("Could not get XY grid from bounds. "
                             "X or Y coordinate doesn't have 2 bounds "
                             "per point.")

    # take a copy of the data so that we can make modifications to it
    data = data.copy()

    # If we are global, then append the first column of data the array to the
    # last (and add 360 degrees) NOTE: if it is found that this block of code
    # is useful in anywhere other than this plotting routine, it may be better
    # placed in the CS.
    x_coord = cube.coord(axis="X")
    if getattr(x_coord, 'circular', False):
        _, direction = iris.util.monotonic(x_coord.points,
                                           return_direction=True)
        y = np.append(y, y[:, 0:1], axis=1)
        x = np.append(x, x[:, 0:1] + 360 * direction, axis=1)
        data = ma.concatenate([data, data[:, 0:1]], axis=1)

    # Replace non-cartopy subplot/axes with a cartopy alternative.
    cs = cube.coord_system('CoordSystem')
    if cs:
        cartopy_proj = cs.as_cartopy_projection()
    else:
        cartopy_proj = cartopy.crs.PlateCarree()
    ax = _get_cartopy_axes(cartopy_proj)

    draw_method = getattr(ax, draw_method_name)

    # Set the "from transform" keyword.
    # NB. While cartopy doesn't support spherical contours, just use the
    # projection as the source CRS.
    assert 'transform' not in kwargs, 'Transform keyword is not allowed.'
    kwargs['transform'] = cartopy_proj

    if arg_func is not None:
        new_args, kwargs = arg_func(x, y, data, *args, **kwargs)
    else:
        new_args = (x, y, data) + args

    # Draw the contour lines/filled contours.
    return draw_method(*new_args, **kwargs)