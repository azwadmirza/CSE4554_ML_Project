def guard_transform(transform):
    """Return an Affine transformation instance"""
    if not isinstance(transform, Affine):
        if tastes_like_gdal(transform):
            warnings.warn(
                "GDAL-style transforms are deprecated and will not "
                "be supported in Rasterio 1.0.",
                FutureWarning,
                stacklevel=2)
            transform = Affine.from_gdal(*transform)
        else:
            transform = Affine(*transform)
    a, e = transform.a, transform.e
    if a == 0.0 or e == 0.0:
        raise ValueError(
            "Transform has invalid coefficients a, e: (%f, %f)" % (
                transform.a, transform.e))
    return transform