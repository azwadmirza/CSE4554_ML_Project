def _draw_2d_from_points(draw_method_name, arg_func, cube, *args, **kwargs):
    # NB. In the interests of clarity we use "u" and "v" to refer to the
    # horizontal and vertical axes on the matplotlib plot.
    mode = iris.coords.POINT_MODE
    # Get & remove the coords entry from kwargs.
    coords = kwargs.pop('coords', None)
    if coords is not None:
        plot_defn = _get_plot_defn_custom_coords_picked(cube, coords, mode)
    else:
        plot_defn = _get_plot_defn(cube, mode, ndims=2)

    if _can_draw_map(plot_defn.coords):
        result = _map_common(draw_method_name, arg_func,
                             iris.coords.POINT_MODE, cube, plot_defn,
                             *args, **kwargs)
    else:
        # Obtain data array.
        data = cube.data
        if plot_defn.transpose:
            data = data.T

        # Obtain U and V coordinates
        v_coord, u_coord = plot_defn.coords
        if u_coord:
            u = u_coord.points
            u = _fixup_dates(u_coord, u)
        else:
            u = np.arange(data.shape[1])
        if v_coord:
            v = v_coord.points
            v = _fixup_dates(v_coord, v)
        else:
            v = np.arange(data.shape[0])

        if plot_defn.transpose:
            u = u.T
            v = v.T

        if u.dtype == np.dtype(object) and isinstance(u[0], datetime.datetime):
            u = mpl_dates.date2num(u)

        if v.dtype == np.dtype(object) and isinstance(v[0], datetime.datetime):
            v = mpl_dates.date2num(v)

        u, v = _broadcast_2d(u, v)

        draw_method = getattr(plt, draw_method_name)
        if arg_func is not None:
            args, kwargs = arg_func(u, v, data, *args, **kwargs)
            result = draw_method(*args, **kwargs)
        else:
            result = draw_method(u, v, data, *args, **kwargs)

    return result