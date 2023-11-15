def get_area_file():
    """Find area file(s) to use.

    The files are to be named `areas.yaml` or `areas.def`.
    """
    paths = config_search_paths('areas.yaml')
    if paths:
        return paths
    else:
        return get_config_path('areas.def')