def hgc_to_hgs(hgccoord, hgsframe):
    """
    Convert from Heliograpic Carrington to Heliographic Stonyhurst.
    """
    if hgsframe.obstime is None or np.any(hgsframe.obstime != hgccoord.obstime):
        raise ValueError("Can not transform from Heliographic Carrington to "
                         "Heliographic Stonyhurst, unless both frames have matching obstime.")
    obstime = hgsframe.obstime
    s_lon = hgccoord.spherical.lon - _carrington_offset(obstime).to(
        u.deg)
    representation = SphericalRepresentation(s_lon, hgccoord.spherical.lat,
                                             hgccoord.spherical.distance)

    return hgsframe.realize_frame(representation)