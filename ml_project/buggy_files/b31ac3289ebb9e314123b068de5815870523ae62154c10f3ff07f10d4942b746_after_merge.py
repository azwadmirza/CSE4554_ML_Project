def chmodAsParent(child_path):
    """Retain permissions of parent for childs.

    (Does not work for Windows hosts)
    :param child_path: Child Path to change permissions to sync from parent
    :type child_path: str
    """
    if os.name == 'nt' or os.name == 'ce':
        return

    parent_path = ek(os.path.dirname, child_path)

    if not parent_path:
        logger.debug(u'No parent path provided in {path}, unable to get permissions from it', path=child_path)
        return

    child_path = ek(os.path.join, parent_path, ek(os.path.basename, child_path))

    if not ek(os.path.exists, child_path):
        return

    parent_path_stat = ek(os.stat, parent_path)
    parent_mode = stat.S_IMODE(parent_path_stat[stat.ST_MODE])

    child_path_stat = ek(os.stat, child_path.encode(sickbeard.SYS_ENCODING))
    child_path_mode = stat.S_IMODE(child_path_stat[stat.ST_MODE])

    if ek(os.path.isfile, child_path):
        child_mode = fileBitFilter(parent_mode)
    else:
        child_mode = parent_mode

    if child_path_mode == child_mode:
        return

    child_path_owner = child_path_stat.st_uid
    user_id = os.geteuid()

    if user_id not in (0, child_path_owner):
        logger.debug(u'Not running as root or owner of {path}, not trying to set permissions', path=child_path)
        return

    try:
        ek(os.chmod, child_path, child_mode)
        logger.debug(u'Setting permissions for {path} to {mode} as parent directory has {parent_mode}',
                     path=child_path, mode=child_mode, parent_mode=parent_mode)
    except OSError:
        logger.debug(u'Failed to set permission for {path} to {mode}', path=child_path, mode=child_mode)