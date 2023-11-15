def utils_rename(c, src, dst, verbose=True):
    """Platform independent rename."""
    # Don't call g.makeAllNonExistentDirectories.
    # It's not right to do this here!!
    # head, tail = g.os_path_split(dst)
    # if head: g.makeAllNonExistentDirectories(head,c=c)
    try:
        shutil.move(src, dst)
        return True
    except Exception:
        if verbose:
            g.error('exception renaming', src, 'to', dst)
            g.es_exception(full=False)
        return False