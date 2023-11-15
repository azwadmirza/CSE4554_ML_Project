def ensure_ring(geom, values=None):
    """Ensure the (multi-)geometry forms a ring.

    Checks the start- and end-point of each geometry to ensure they
    form a ring, if not the start point is inserted at the end point.
    If a values array is provided (which must match the geometry in
    length) then the insertion will occur on the values instead,
    ensuring that they will match the ring geometry.

    Args:
        geom: 2-D array of geometry coordinates
        values: Optional array of values

    Returns:
        Array where values have been inserted and ring closing indexes
    """
    if values is None:
        values = geom
    breaks = np.where(np.isnan(geom).sum(axis=1))[0]
    starts = [0] + list(breaks+1)
    ends = list(breaks-1) + [len(geom)-1]
    zipped = zip(geom[starts], geom[ends], ends, values[starts])
    unpacked = tuple(zip(*[(v, i+1) for s, e, i, v in zipped
                     if (s!=e).any()]))
    if not unpacked:
        return values
    inserts, inds = unpacked
    return np.insert(values, list(inds), list(inserts), axis=0)