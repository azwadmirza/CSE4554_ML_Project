def xyz2angle(x, y, z):
    """Convert cartesian to azimuth and zenith."""
    azi = np.rad2deg(np.arctan2(x, y))
    zen = 90 - np.rad2deg(np.arctan2(z, np.sqrt(x**2 + y**2)))
    return azi, zen