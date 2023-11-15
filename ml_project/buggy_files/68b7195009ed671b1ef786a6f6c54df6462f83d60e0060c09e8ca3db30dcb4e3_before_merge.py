def set_data_dir(proj_data_dir):
    """
    Set the data directory for PROJ to use.

    Parameters
    ----------
    proj_data_dir: str
        The path to rhe PROJ data directory.
    """
    global _USER_PROJ_DATA
    global _VALIDATED_PROJ_DATA
    _USER_PROJ_DATA = proj_data_dir
    # set to none to re-validate
    _VALIDATED_PROJ_DATA = None