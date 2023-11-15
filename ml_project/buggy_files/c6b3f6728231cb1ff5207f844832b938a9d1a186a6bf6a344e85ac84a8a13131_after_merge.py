def hgs_to_hgc(hgscoord, hgcframe):
    """
    Transform from Heliographic Stonyhurst to Heliograpic Carrington.
    """
    if hgcframe.obstime is None or np.any(hgcframe.obstime != hgscoord.obstime):
        raise ValueError("Can not transform from Heliographic Stonyhurst to "
                         "Heliographic Carrington, unless both frames have matching obstime.")

    c_lon = hgscoord.spherical.lon + _carrington_offset(hgscoord.obstime).to(u.deg)
    representation = SphericalRepresentation(c_lon, hgscoord.spherical.lat,
                                             hgscoord.spherical.distance)
    hgcframe = hgcframe.__class__(obstime=hgscoord.obstime)

    return hgcframe.realize_frame(representation)