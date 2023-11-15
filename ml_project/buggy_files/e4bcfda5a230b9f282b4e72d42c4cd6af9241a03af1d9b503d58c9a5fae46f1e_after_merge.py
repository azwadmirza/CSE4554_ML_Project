def xyz2lonlat(x, y, z):
    """Convert cartesian to lon lat."""
    lon = xu.rad2deg(xu.arctan2(y, x))
    lat = xu.rad2deg(xu.arctan2(z, xu.sqrt(x**2 + y**2)))
    return lon, lat