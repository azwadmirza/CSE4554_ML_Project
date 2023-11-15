def omerc2cf(area):
    """Return the cf grid mapping for the omerc projection."""
    proj_dict = area.proj_dict

    args = dict(azimuth_of_central_line=proj_dict.get('alpha'),
                latitude_of_projection_origin=proj_dict.get('lat_0'),
                longitude_of_projection_origin=proj_dict.get('lonc'),
                grid_mapping_name='oblique_mercator',
                reference_ellipsoid_name=proj_dict.get('ellps', 'WGS84'),
                false_easting=0.,
                false_northing=0.
                )
    if "no_rot" in proj_dict:
        args['no_rotation'] = 1
    if "gamma" in proj_dict:
        args['gamma'] = proj_dict['gamma']
    return args