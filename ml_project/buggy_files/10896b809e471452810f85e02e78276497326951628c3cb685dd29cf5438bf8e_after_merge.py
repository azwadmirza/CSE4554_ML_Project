def lonlat2xyz(lon, lat):
    """Convert lon lat to cartesian."""
    lat = xu.deg2rad(lat)
    lon = xu.deg2rad(lon)
    x = xu.cos(lat) * xu.cos(lon)
    y = xu.cos(lat) * xu.sin(lon)
    z = xu.sin(lat)
    return x, y, z