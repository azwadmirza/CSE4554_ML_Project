def set_data_dir(proj_data_dir):
    """
    Set the data directory for PROJ to use.

    Parameters
    ----------
    proj_data_dir: str
        The path to rhe PROJ data directory.
    """
    global _USER_PROJ_DATA
    _USER_PROJ_DATA = proj_data_dir
    # reset search paths
    from pyproj._datadir import PYPROJ_CONTEXT

    PYPROJ_CONTEXT.set_search_paths(reset=True)