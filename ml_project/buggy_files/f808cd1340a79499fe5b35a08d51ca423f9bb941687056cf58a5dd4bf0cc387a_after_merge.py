def write_item_mtime(item, mtime):
    """Write the given mtime to an item's `mtime` field and to the mtime of the
    item's file.
    """
    if mtime is None:
        log.warn(u"No mtime to be preserved for item '{0}'"
                 .format(util.displayable_path(item.path)))
        return

    # The file's mtime on disk must be in sync with the item's mtime
    write_file_mtime(util.syspath(item.path), mtime)
    item.mtime = mtime