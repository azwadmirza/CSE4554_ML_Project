def update_item_times(lib, item):
    mtime = item_mtime[item.path]
    if mtime is not None:
        item.added = mtime
        if config['importadded']['preserve_mtimes'].get(bool):
            write_item_mtime(item, mtime)
        item.store()
        del item_mtime[item.path]