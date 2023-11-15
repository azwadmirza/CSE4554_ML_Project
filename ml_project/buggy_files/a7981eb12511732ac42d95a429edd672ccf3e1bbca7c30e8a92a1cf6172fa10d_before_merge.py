def is_collection_path(path):
    """
    Verify that a path meets min requirements to be a collection
    :param path: byte-string path to evaluate for collection containment
    :return: boolean signifying 'collectionness'
    """

    is_coll = False
    if os.path.isdir(path):
        for flag in FLAG_FILES:
            if os.path.exists(os.path.join(path, flag)):
                is_coll = True
                break

    return is_coll