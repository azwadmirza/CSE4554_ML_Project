def laea2cf(area):
    """Return the cf grid mapping for the laea projection."""
    proj_dict = area.proj_dict
    args = dict(latitude_of_projection_origin=proj_dict.get('lat_0'),
                longitude_of_projection_origin=proj_dict.get('lon_0'),
                grid_mapping_name='lambert_azimuthal_equal_area',
                )
    return args