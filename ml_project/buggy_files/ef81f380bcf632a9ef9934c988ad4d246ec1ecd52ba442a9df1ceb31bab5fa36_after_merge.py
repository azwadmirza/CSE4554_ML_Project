def angle2xyz(azi, zen):
    """Convert azimuth and zenith to cartesian."""
    azi = xu.deg2rad(azi)
    zen = xu.deg2rad(zen)
    x = xu.sin(zen) * xu.sin(azi)
    y = xu.sin(zen) * xu.cos(azi)
    z = xu.cos(zen)
    return x, y, z