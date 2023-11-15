def chmod(path, mode):
    if not os.path.exists(path):
        logger.error("Path does not exist: {0}".format(path))
    else:
        os.chmod(path, mode)