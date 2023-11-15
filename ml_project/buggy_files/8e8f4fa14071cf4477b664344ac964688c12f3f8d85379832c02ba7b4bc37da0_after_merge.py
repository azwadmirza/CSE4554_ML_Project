def _map_common(draw_method_name, arg_func, mode, cube, plot_defn,
                *args, **kwargs):
    """
    Draw the given cube on a map using its points or bounds.

    "Mode" parameter will switch functionality between POINT or BOUND plotting.


    """
    # Generate 2d x and 2d y grids.
    y_coord, x_coord = plot_defn.coords
    if mode == iris.coords.POINT_MODE:
        if x_coord.ndim == y_coord.ndim == 1:
            x, y = np.meshgrid(x_coord.points, y_coord.points)
        elif x_coord.ndim == y_coord.ndim == 2:
            x = x_coord.points
            y = y_coord.points
        else:
            raise ValueError("Expected 1D or 2D XY coords")
    else:
        try:
            x, y = np.meshgrid(x_coord.contiguous_bounds(),
                               y_coord.contiguous_bounds())
        # Exception translation.
        except iris.exceptions.CoordinateMultiDimError:
            raise ValueError("Could not get XY grid from bounds. "
                             "X or Y coordinate not 1D.")
        except ValueError:
            raise ValueError("Could not get XY grid from bounds. "
                             "X or Y coordinate doesn't have 2 bounds "
                             "per point.")

    # Obtain the data array.
    data = cube.data
    if plot_defn.transpose:
        data = data.T

    # If we are global, then append the first column of data the array to the
    # last (and add 360 degrees) NOTE: if it is found that this block of code
    # is useful in anywhere other than this plotting routine, it may be better
    # placed in the CS.
    if getattr(x_coord, 'circular', False):
        _, direction = iris.util.monotonic(x_coord.points,
                                           return_direction=True)
        y = np.append(y, y[:, 0:1], axis=1)
        x = np.append(x, x[:, 0:1] + 360 * direction, axis=1)
        data = ma.concatenate([data, data[:, 0:1]], axis=1)

    # Replace non-cartopy subplot/axes with a cartopy alternative.
    if x_coord.coord_system != y_coord.coord_system:
        raise ValueError('The X and Y coordinates must have equal coordinate'
                         ' systems.')
    cs = x_coord.coord_system
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