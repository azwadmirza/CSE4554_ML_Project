def laea2cf(proj_dict):
    """Return the cf grid mapping for the laea projection."""
    grid_mapping_name = 'lambert_azimuthal_equal_area'

    args = dict(latitude_of_projection_origin=proj_dict.get('lat_0'),
                longitude_of_projection_origin=proj_dict.get('lon_0'),
                crtype='grid_mapping',
                coords=['projection_x_coordinate', 'projection_y_coordinate'])
    return cf.CoordinateReference(grid_mapping_name, **args)