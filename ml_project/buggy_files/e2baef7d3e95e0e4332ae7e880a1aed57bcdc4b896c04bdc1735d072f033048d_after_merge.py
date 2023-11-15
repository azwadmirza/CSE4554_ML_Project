def xyz2angle(x, y, z):
    """Convert cartesian to azimuth and zenith."""
    azi = xu.rad2deg(xu.arctan2(x, y))
    zen = 90 - xu.rad2deg(xu.arctan2(z, xu.sqrt(x**2 + y**2)))
    return azi, zen