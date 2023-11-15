def update_item_times(lib, item):
    if reimported_item(item):
        log.debug(u"Item '{0}' is reimported, skipping import of added "
                  u"date.".format(util.displayable_path(item.path)))
        return
    mtime = item_mtime.pop(item.path, None)
    if mtime:
        item.added = mtime
        if config['importadded']['preserve_mtimes'].get(bool):
            write_item_mtime(item, mtime)
        log.debug(u"Import of item '{0}', selected item.added={1}"
                  .format(util.displayable_path(item.path), item.added))
        item.store()