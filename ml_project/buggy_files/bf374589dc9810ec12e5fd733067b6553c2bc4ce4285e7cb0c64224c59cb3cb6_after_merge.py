def update_album_times(lib, album):
    if reimported_album(album):
        log.debug(u"Album '{0}' is reimported, skipping import of added dates"
                  u" for the album and its items."
                  .format(util.displayable_path(album.path)))
        return

    album_mtimes = []
    for item in album.items():
        mtime = item_mtime.pop(item.path, None)
        if mtime:
            album_mtimes.append(mtime)
            if config['importadded']['preserve_mtimes'].get(bool):
                write_item_mtime(item, mtime)
                item.store()
    album.added = min(album_mtimes)
    log.debug(u"Import of album '{0}', selected album.added={1} from item"
              u" file mtimes.".format(album.album, album.added))
    album.store()