def xyz2lonlat(x, y, z):
    """Convert cartesian to lon lat."""
    lon = np.rad2deg(np.arctan2(y, x))
    lat = np.rad2deg(np.arctan2(z, np.sqrt(x**2 + y**2)))
    return lon, lat