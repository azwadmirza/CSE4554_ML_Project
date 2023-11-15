def create_grid_mapping(area):
    """Create the grid mapping instance for `area`."""
    try:
        grid_mapping = mappings[area.proj_dict['proj']](area)
        grid_mapping['name'] = area.proj_dict['proj']
    except KeyError:
        raise NotImplementedError

    return grid_mapping