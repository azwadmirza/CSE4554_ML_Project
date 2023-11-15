def file_list(load):
    """
    Return a list of all files on the file server in a specified environment
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
    for bucket in _find_files(metadata[saltenv]):
        for buckets in six.itervalues(bucket):
            files = [f for f in buckets if not fs.is_file_ignored(__opts__, f)]
            ret += _trim_env_off_path(files, saltenv)

    return ret