def geos_linearring_from_py(ob, update_geom=None, update_ndim=0):
    # If a LinearRing is passed in, clone it and return
    # If a LineString is passed in, clone the coord seq and return a
    # LinearRing.
    #
    # NB: access to coordinates using the array protocol has been moved
    # entirely to the speedups module.

    if isinstance(ob, LineString):
        if type(ob) == LinearRing:
            return geos_geom_from_py(ob)
        elif ob.is_closed and len(ob.coords) >= 4:
            return geos_geom_from_py(ob, lgeos.GEOSGeom_createLinearRing)
        else:
            ob = list(ob.coords)

    try:
        m = len(ob)
    except TypeError:  # Iterators, e.g. Python 3 zip
        ob = list(ob)
        m = len(ob)

    if m == 0:
        return None

    def _coords(o):
        if isinstance(o, Point):
            return o.coords[0]
        else:
            return o

    n = len(_coords(ob[0]))
    if m < 3:
        raise ValueError(
            "A LinearRing must have at least 3 coordinate tuples")
    assert (n == 2 or n == 3)

    # Add closing coordinates if not provided
    if (
        m == 3
        or _coords(ob[0])[0] != _coords(ob[-1])[0]
        or _coords(ob[0])[1] != _coords(ob[-1])[1]
    ):
        M = m + 1
    else:
        M = m

    # Create a coordinate sequence
    if update_geom is not None:
        if n != update_ndim:
            raise ValueError(
                "Coordinate dimensions mismatch: target geom has {} dims, "
                "update geom has {} dims".format(n, update_ndim))
        cs = lgeos.GEOSGeom_getCoordSeq(update_geom)
    else:
        cs = lgeos.GEOSCoordSeq_create(M, n)

    # add to coordinate sequence
    for i in range(m):
        coords = _coords(ob[i])
        # Because of a bug in the GEOS C API,
        # always set X before Y
        lgeos.GEOSCoordSeq_setX(cs, i, coords[0])
        lgeos.GEOSCoordSeq_setY(cs, i, coords[1])
        if n == 3:
            try:
                lgeos.GEOSCoordSeq_setZ(cs, i, coords[2])
            except IndexError:
                raise ValueError("Inconsistent coordinate dimensionality")

    # Add closing coordinates to sequence?
    if M > m:
        coords = _coords(ob[0])
        # Because of a bug in the GEOS C API,
        # always set X before Y
        lgeos.GEOSCoordSeq_setX(cs, M-1, coords[0])
        lgeos.GEOSCoordSeq_setY(cs, M-1, coords[1])
        if n == 3:
            lgeos.GEOSCoordSeq_setZ(cs, M-1, coords[2])

    if update_geom is not None:
        return None
    else:
        return lgeos.GEOSGeom_createLinearRing(cs), n