def create_ternary_contour(coordinates, values, pole_labels=['a', 'b', 'c'],
                           tooltip_mode='proportions', width=500, height=500,
                           ncontours=None,
                           showscale=False,
                           coloring=None,
                           colorscale=None,
                           plot_bgcolor='rgb(240,240,240)',
                           title=None):
    """
    Ternary contour plot.

    Parameters
    ----------

    coordinates : list or ndarray
        Barycentric coordinates of shape (2, N) or (3, N) where N is the
        number of data points. The sum of the 3 coordinates is expected
        to be 1 for all data points.
    values : array-like
        Data points of field to be represented as contours.
    pole_labels : str, default ['a', 'b', 'c']
        Names of the three poles of the triangle.
    tooltip_mode : str, 'proportions' or 'percents'
        Coordinates inside the ternary plot can be displayed either as
        proportions (adding up to 1) or as percents (adding up to 100).
    width : int
        Figure width.
    height : int
        Figure height.
    ncontours : int or None
        Number of contours to display (determined automatically if None).
    showscale : bool, default False
        If True, a colorbar showing the color scale is displayed.
    coloring : None or 'lines'
        How to display contour. Filled contours if None, lines if ``lines``.
    colorscale : None or array-like
        colorscale of the contours.
    plot_bgcolor :
        color of figure background
    title : str or None
        Title of ternary plot

    Examples
    ========

    Example 1: ternary contour plot with filled contours

    # Define coordinates
    a, b = np.mgrid[0:1:20j, 0:1:20j]
    mask = a + b <= 1
    a = a[mask].ravel()
    b = b[mask].ravel()
    c = 1 - a - b
    # Values to be displayed as contours
    z = a * b * c
    fig = ff.create_ternary_contour(np.stack((a, b, c)), z)

    It is also possible to give only two barycentric coordinates for each
    point, since the sum of the three coordinates is one:

    fig = ff.create_ternary_contour(np.stack((a, b)), z)

    Example 2: ternary contour plot with line contours

    fig = ff.create_ternary_contour(np.stack((a, b)), z, coloring='lines')
    """
    if interpolate is None:
        raise ImportError("""\
The create_ternary_contour figure factory requires the scipy package""")

    grid_z, gr_x, gr_y, tooltip = _compute_grid(coordinates, values,
                                                tooltip_mode)

    x_ticks, y_ticks, posx, posy = _cart_coord_ticks(t=0.01)

    layout = _ternary_layout(pole_labels=pole_labels,
                             width=width, height=height, title=title,
                             plot_bgcolor=plot_bgcolor)

    annotations = _set_ticklabels(layout['annotations'], posx, posy,
                                  proportions=True)
    if colorscale is None:
        colorscale = _pl_deep()

    contour_trace = _contour_trace(gr_x, gr_y, grid_z, tooltip,
                                   ncontours=ncontours,
                                   showscale=showscale,
                                   colorscale=colorscale,
                                   coloring=coloring)
    side_trace, tick_trace = _styling_traces_ternary(x_ticks, y_ticks)
    fig = go.Figure(data=[contour_trace,  tick_trace, side_trace],
                    layout=layout)
    fig.layout.annotations = annotations
    return fig