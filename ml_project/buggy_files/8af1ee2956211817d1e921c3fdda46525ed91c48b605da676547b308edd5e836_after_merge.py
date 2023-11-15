def _compute_grid(coordinates, values, tooltip_mode):
    """
    Compute interpolation of data points on regular grid in Cartesian
    coordinates.

    Parameters
    ==========

    coordinates : array-like
        Barycentric coordinates of data points.
    values : 1-d array-like
        Data points, field to be represented as contours.
    tooltip_mode : str, 'proportions' or 'percents'
        Coordinates inside the ternary plot can be displayed either as
        proportions (adding up to 1) or as percents (adding up to 100).
    """
    A, B, C = _prepare_barycentric_coord(coordinates)
    M, invM = _transform_barycentric_cartesian()
    cartes_coord_points = np.einsum('ik, kj -> ij', M, np.stack((A, B, C)))
    xx, yy = cartes_coord_points[:2]
    x_min, x_max = xx.min(), xx.max()
    y_min, y_max = yy.min(), yy.max()
    # n_interp = max(100, int(np.sqrt(len(values))))
    n_interp = 20
    gr_x = np.linspace(x_min, x_max, n_interp)
    gr_y = np.linspace(y_min, y_max, n_interp)
    grid_x, grid_y = np.meshgrid(gr_x, gr_y)
    grid_z = interpolate.griddata(
        cartes_coord_points[:2].T, values, (grid_x, grid_y), method='cubic')
    bar_coords = np.einsum('ik, kmn -> imn', invM,
                           np.stack((grid_x, grid_y, np.ones(grid_x.shape))))
    # invalidate the points outside of the reference triangle
    bar_coords[np.where(bar_coords < 0)] = 0  # None
    # recompute back cartesian coordinates with invalid positions
    xy1 = np.einsum('ik, kmn -> imn', M, bar_coords)
    is_nan = np.where(np.isnan(xy1[0]))
    grid_z[is_nan] = 0  # None
    tooltip = _tooltip(n_interp, bar_coords, grid_z, xy1, tooltip_mode)
    return grid_z, gr_x, gr_y, tooltip