def makeAllNonExistentDirectories(theDir, c=None, force=False, verbose=True):
    """
    Attempt to make all non-existent directories.
    Return the created directory, or None.
    
    If c is given, support {{expressions}}.
    
    A wrapper from os.makedirs (new in Python 3.2).
    
    """
    if force:
        # Bug fix: g.app.config will not exist during startup.
        create = True
    elif c:
        create = c and c.config and c.config.create_nonexistent_directories
    else:
        create = (g.app and g.app.config and
            g.app.config.create_nonexistent_directories)
    if c:
        theDir = c.expand_path_expression(theDir)
    #
    # Return True if the directory already exists.
    theDir = g.os_path_normpath(theDir)
    exists = g.os_path_isdir(theDir) and g.os_path_exists(theDir)
    if exists:
        return theDir
    #
    # Return False if we aren't forcing the create.
    if not force and not create:
        return None
    #
    # #1450: Just use os.makedirs.
    try:
        os.makedirs(theDir, mode=0o777, exist_ok=False)
        return theDir
    except Exception:
        return None