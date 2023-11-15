def makeAllNonExistentDirectories(theDir, c=None, force=False, verbose=True):
    """Attempt to make all non-existent directories"""
    testing = False  # True: don't actually make the directories.
    if force:
        create = True  # Bug fix: g.app.config will not exist during startup.
    elif c:
        create = c.config and c.config.create_nonexistent_directories
    else:
        create = (g.app and g.app.config and
            g.app.config.create_nonexistent_directories)
    if c:
        theDir = c.expand_path_expression(theDir)
    dir1 = theDir = g.os_path_normpath(theDir)
    ok = g.os_path_isdir(dir1) and g.os_path_exists(dir1)
    if ok:
        return ok
    if not force and not create:
        return False
    # Split theDir into all its component parts.
    paths = []
    while theDir:
        head, tail = g.os_path_split(theDir)
        if tail:
            paths.append(tail)
            theDir = head
        else:
            paths.append(head)
            break
    path = ""
    paths.reverse()
    for s in paths:
        path = g.os_path_finalize_join(path, s)
        if not g.os_path_exists(path):
            try:
                if testing:
                    g.trace('***making', path)
                else:
                    os.mkdir(path)
                if verbose and not testing and not g.app.unitTesting:
                    g.red("created directory:", path)
            except Exception:
                if verbose: g.error("exception creating directory:", path)
                g.es_exception()
                return None
    return dir1  # All have been created.