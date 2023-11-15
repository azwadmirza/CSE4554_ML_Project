def points_from_xy(x, y, z=None):
    """Convert arrays of x and y values to a GeometryArray of points."""
    x = np.asarray(x, dtype="float64")
    y = np.asarray(y, dtype="float64")
    if z is not None:
        z = np.asarray(z, dtype="float64")
    out = _points_from_xy(x, y, z)
    out = np.array(out, dtype=object)
    return GeometryArray(out)