def update_album_times(lib, album):
    album_mtimes = []
    for item in album.items():
        mtime = item_mtime[item.path]
        if mtime is not None:
            album_mtimes.append(mtime)
            if config['importadded']['preserve_mtimes'].get(bool):
                write_item_mtime(item, mtime)
                item.store()
            del item_mtime[item.path]

    album.added = min(album_mtimes)
    album.store()