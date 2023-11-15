def from_wkt(data):
    """
    Convert a list or array of WKT objects to a GeometryArray.
    """
    import shapely.wkt

    n = len(data)

    out = []

    for idx in range(n):
        geom = data[idx]
        if geom is not None and len(geom):
            if isinstance(geom, bytes):
                geom = geom.decode("utf-8")
            geom = shapely.wkt.loads(geom)
        else:
            geom = None
        out.append(geom)

    out = np.array(out, dtype=object)
    return GeometryArray(out)