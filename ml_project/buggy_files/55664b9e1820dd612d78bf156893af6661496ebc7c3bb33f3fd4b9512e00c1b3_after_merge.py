def makeAllNonExistentDirectories(theDir, c=None, force=False, verbose=True):
    """
    Attempt to make all non-existent directories.
    
    A wrapper from os.makedirs (new in Python 3.2).
    
    """
    if force:
        create = True  # Bug fix: g.app.config will not exist during startup.
    elif c:
        create = c.config and c.config.create_nonexistent_directories
    else:
        create = (g.app and g.app.config and
            g.app.config.create_nonexistent_directories)
    if c:
        theDir = c.expand_path_expression(theDir)
    #
    # Return True if the directory already exists.
    dir1 = theDir = g.os_path_normpath(theDir)
    exists = g.os_path_isdir(dir1) and g.os_path_exists(dir1)
    if exists:
        return True
    #
    # Return False if we aren't forcing the create.
    if not force and not create:
        return False
    #
    # Just use os.makedirs.
    try:
        os.makedirs(theDir, mode=0o777, exist_ok=False)
        return True
    except Exception:
        return False