def from_wkb(data):
    """
    Convert a list or array of WKB objects to a GeometryArray.
    """
    import shapely.wkb

    n = len(data)

    out = []

    for idx in range(n):
        geom = data[idx]
        if geom is not None and len(geom):
            geom = shapely.wkb.loads(geom)
        else:
            geom = None
        out.append(geom)

    aout = np.empty(n, dtype=object)
    aout[:] = out
    return GeometryArray(aout)