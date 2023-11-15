def _draw_2d_from_bounds(draw_method_name, cube, *args, **kwargs):
    # NB. In the interests of clarity we use "u" and "v" to refer to the
    # horizontal and vertical axes on the matplotlib plot.
    mode = iris.coords.BOUND_MODE
    # Get & remove the coords entry from kwargs.
    coords = kwargs.pop('coords', None)
    if coords is not None:
        plot_defn = _get_plot_defn_custom_coords_picked(cube, coords, mode)
    else:
        plot_defn = _get_plot_defn(cube, mode, ndims=2)

    if _can_draw_map(plot_defn.coords):
        result = _map_common(draw_method_name, None, iris.coords.BOUND_MODE,
                             cube, plot_defn, *args, **kwargs)
    else:
        # Obtain data array.
        data = cube.data
        if plot_defn.transpose:
            data = data.T

        # Obtain U and V coordinates
        v_coord, u_coord = plot_defn.coords

        # XXX: Watch out for non-contiguous bounds.
        if u_coord:
            u = u_coord.contiguous_bounds()
        else:
            u = np.arange(data.shape[1] + 1)
        if v_coord:
            v = v_coord.contiguous_bounds()
        else:
            v = np.arange(data.shape[0] + 1)

        if plot_defn.transpose:
            u = u.T
            v = v.T

        u, v = _broadcast_2d(u, v)
        draw_method = getattr(plt, draw_method_name)
        result = draw_method(u, v, data, *args, **kwargs)

    return result