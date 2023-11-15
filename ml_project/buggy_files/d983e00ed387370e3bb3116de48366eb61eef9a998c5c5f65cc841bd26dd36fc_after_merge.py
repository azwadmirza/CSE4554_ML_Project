def tastes_like_gdal(seq):
    """Return True if `seq` matches the GDAL geotransform pattern."""
    return seq[2] == seq[4] == 0.0 and seq[1] > 0 and seq[5] < 0