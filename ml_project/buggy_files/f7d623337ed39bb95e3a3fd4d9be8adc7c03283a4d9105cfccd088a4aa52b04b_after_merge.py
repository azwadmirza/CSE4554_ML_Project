def browse_folder(_, title):
    """Ask the user to select a folder.  Return full path."""
    pidl = shell.SHBrowseForFolder(None, None, title)[0]
    if pidl is None:
        # user cancelled
        return None
    fullpath = shell.SHGetPathFromIDList(pidl)
    return fullpath