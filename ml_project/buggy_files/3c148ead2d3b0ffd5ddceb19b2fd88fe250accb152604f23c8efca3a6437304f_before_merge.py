def list_valid_collection_paths(search_paths=None, warn=False):
    """
    Filter out non existing or invalid search_paths for collections
    :param search_paths: list of text-string paths, if none load default config
    :param warn: display warning if search_path does not exist
    :return: subset of original list
    """

    if search_paths is None:
        search_paths = AnsibleCollectionLoader().n_collection_paths

    for path in search_paths:

        if not os.path.exists(path):
            # warn for missing, but not if default
            if warn:
                display.warning("The configured collection path {0} does not exist.".format(path))
            continue

        if not os.path.isdir(path):
            if warn:
                display.warning("The configured collection path {0}, exists, but it is not a directory.".format(path))
            continue

        yield path