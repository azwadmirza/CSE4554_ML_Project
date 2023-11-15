def redistribute_vertices(geom, dist):
    """
    Redistribute the vertices on a projected LineString or MultiLineString. The distance
    argument is only approximate since the total distance of the linestring may not be
    a multiple of the preferred distance. This function works on only [Multi]LineString
    geometry types.

    This code is adapted from an answer by Mike T from this original question:
    https://stackoverflow.com/questions/34906124/interpolating-every-x-distance-along-multiline-in-shapely

    Parameters
    ----------
    geom : LineString or MultiLineString
        a Shapely geometry
    dist : float
        spacing length along edges. Units are the same as the geom; Degrees for unprojected geometries and meters
        for projected geometries. The smaller the value, the more points are created.

    Returns
    -------
        list of Point geometries : list
    """
    if geom.geom_type == 'LineString':
        num_vert = int(round(geom.length / dist))
        if num_vert == 0:
            num_vert = 1
        return [geom.interpolate(float(n) / num_vert, normalized=True)
                for n in range(num_vert + 1)]
    elif geom.geom_type == 'MultiLineString':
        parts = [redistribute_vertices(part, dist)
                 for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise ValueError('unhandled geometry {}'.format(geom.geom_type))