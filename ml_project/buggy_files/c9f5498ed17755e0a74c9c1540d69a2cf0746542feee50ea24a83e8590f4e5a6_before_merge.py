def omerc2cf(proj_dict):
    """Return the cf grid mapping for the omerc projection."""
    grid_mapping_name = 'oblique_mercator'

    if "no_rot" in proj_dict:
        no_rotation = " "
    else:
        no_rotation = None

    args = dict(azimuth_of_central_line=proj_dict.get('alpha'),
                latitude_of_projection_origin=proj_dict.get('lat_0'),
                longitude_of_projection_origin=proj_dict.get('lonc'),
                # longitude_of_projection_origin=0.,
                no_rotation=no_rotation,
                # reference_ellipsoid_name=proj_dict.get('ellps'),
                semi_major_axis=6378137.0,
                semi_minor_axis=6356752.3142,
                false_easting=0.,
                false_northing=0.,
                crtype='grid_mapping',
                coords=['projection_x_coordinate', 'projection_y_coordinate'])
    return cf.CoordinateReference(grid_mapping_name, **args)