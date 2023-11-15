def utils_rename(c, src, dst, verbose=True):
    """Platform independent rename."""
    # Don't call g.makeAllNonExistentDirectories here!
    try:
        shutil.move(src, dst)
        return True
    except Exception:
        if verbose:
            g.error('exception renaming', src, 'to', dst)
            g.es_exception(full=False)
        return False