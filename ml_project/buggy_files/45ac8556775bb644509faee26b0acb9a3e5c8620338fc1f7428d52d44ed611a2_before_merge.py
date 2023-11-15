def _get_plot_defn(cube, mode, ndims=2):
    """
    Return data and plot-axis coords given a cube & a mode of either
    POINT_MODE or BOUND_MODE.

    """
    if cube.ndim != ndims:
        msg = 'Cube must be %s-dimensional. Got %s dimensions.'
        raise ValueError(msg % (ndims, cube.data.ndim))

    # Start by taking the DimCoords from each dimension.
    coords = [None] * ndims
    for dim_coord in cube.dim_coords:
        dim = cube.coord_dims(dim_coord)[0]
        coords[dim] = dim_coord

    # When appropriate, restrict to 1D with bounds.
    if mode == iris.coords.BOUND_MODE:
        coords = map(_valid_bound_coord, coords)

    def guess_axis(coord):
        axis = None
        if coord is not None:
            axis = iris.util.guess_coord_axis(coord)
        return axis

    # Allow DimCoords in aux_coords to fill in for missing dim_coords.
    for dim, coord in enumerate(coords):
        if coord is None:
            aux_coords = cube.coords(dimensions=dim)
            aux_coords = filter(lambda coord:
                                isinstance(coord, iris.coords.DimCoord),
                                aux_coords)
            if aux_coords:
                key_func = lambda coord: coord._as_defn()
                aux_coords.sort(key=key_func)
                coords[dim] = aux_coords[0]

    if mode == iris.coords.POINT_MODE:
        # Allow multi-dimensional aux_coords to override the dim_coords.
        # (things like grid_latitude will be overriden by latitude etc.)
        axes = map(guess_axis, coords)
        for coord in cube.coords(dim_coords=False):
            if max(coord.shape) > 1 and (mode == iris.coords.POINT_MODE or
                                         coord.nbounds):
                axis = iris.util.guess_coord_axis(coord)
                if axis and axis in axes:
                    coords[axes.index(axis)] = coord

    # Re-order the coordinates to achieve the preferred
    # horizontal/vertical associations.
    def sort_key(coord):
        order = {'X': 2, 'T': 1, 'Y': -1, 'Z': -2}
        axis = guess_axis(coord)
        return (order.get(axis, 0), coord and coord.name())
    sorted_coords = sorted(coords, key=sort_key)

    transpose = (sorted_coords != coords)
    return PlotDefn(sorted_coords, transpose)