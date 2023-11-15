def record_import_mtime(item, source, destination):
    """Record the file mtime of an item's path before import.
    """
    if (source == destination):
        # Re-import of an existing library item?
        return

    mtime = os.stat(util.syspath(source)).st_mtime
    item_mtime[destination] = mtime
    log.debug(u"Recorded mtime {0} for item '{1}' imported from '{2}'".format(
        mtime, util.displayable_path(destination),
        util.displayable_path(source)))