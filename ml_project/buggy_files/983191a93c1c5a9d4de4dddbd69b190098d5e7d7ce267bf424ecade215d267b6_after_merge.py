def dir_list(load):
    """
    Return a list of all directories on the master
    """
    if "env" in load:
        # "env" is not supported; Use "saltenv".
        load.pop("env")

    ret = []

    if "saltenv" not in load:
        return ret

    saltenv = load["saltenv"]
    metadata = _init()

    if not metadata or saltenv not in metadata:
        return ret

    # grab all the dirs from the buckets cache file
    for bucket in _find_dirs(metadata[saltenv]):
        for dirs in bucket.values():
            # trim env and trailing slash
            dirs = _trim_env_off_path(dirs, saltenv, trim_slash=True)
            # remove empty string left by the base env dir in single bucket mode
            ret += [_f for _f in dirs if _f]

    return ret