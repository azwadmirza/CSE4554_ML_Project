def list_collection_dirs(search_paths=None, coll_filter=None):
    """
    Return paths for the specific collections found in passed or configured search paths
    :param search_paths: list of text-string paths, if none load default config
    :param coll_filter: limit collections to just the specific namespace or collection, if None all are returned
    :return: list of collection directory paths
    """

    collections = defaultdict(dict)
    for path in list_valid_collection_paths(search_paths):

        if os.path.isdir(path):
            coll_root = os.path.join(path, 'ansible_collections')

            if os.path.exists(coll_root) and os.path.isdir(coll_root):

                coll = None
                if coll_filter is None:
                    namespaces = os.listdir(coll_root)
                else:
                    if '.' in coll_filter:
                        (nsp, coll) = coll_filter.split('.')
                    else:
                        nsp = coll_filter
                    namespaces = [nsp]

                for ns in namespaces:
                    namespace_dir = os.path.join(coll_root, ns)

                    if os.path.isdir(namespace_dir):

                        if coll is None:
                            colls = os.listdir(namespace_dir)
                        else:
                            colls = [coll]

                        for collection in colls:

                            # skip dupe collections as they will be masked in execution
                            if collection not in collections[ns]:
                                coll_dir = os.path.join(namespace_dir, collection)
                                if is_collection_path(coll_dir):
                                    cpath = os.path.join(namespace_dir, collection)
                                    collections[ns][collection] = cpath
                                    yield cpath