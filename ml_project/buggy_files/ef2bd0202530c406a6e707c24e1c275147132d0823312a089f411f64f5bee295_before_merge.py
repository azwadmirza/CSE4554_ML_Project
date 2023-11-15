def create_grid_mapping(area):
    """Create the grid mapping instance for `area`."""

    try:
        grid_mapping = mappings[area.proj_dict['proj']](area.proj_dict)
    except KeyError:
        raise NotImplementedError

    return grid_mapping