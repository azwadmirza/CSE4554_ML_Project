def chowner(path, owner):
    if not os.path.exists(path):
        logger.error("Path does not exist: {0}".format(path))
    else:
        owner_info = pwd.getpwnam(owner)
        os.chown(path, owner_info[2], owner_info[3])