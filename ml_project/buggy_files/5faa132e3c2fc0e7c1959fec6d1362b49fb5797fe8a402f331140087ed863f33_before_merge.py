def os_path_finalize(path, **keys):
    """
    Expand '~', then return os.path.normpath, os.path.abspath of the path.
    There is no corresponding os.path method
    """
    path = path.replace('\x00','') # Fix Pytyon 3 bug on Windows 10.
    path = os.path.abspath(path)
    path = os.path.normpath(path)
    if g.isWindows:
        path = path.replace('\\','/')
    # calling os.path.realpath here would cause problems in some situations.
    return path