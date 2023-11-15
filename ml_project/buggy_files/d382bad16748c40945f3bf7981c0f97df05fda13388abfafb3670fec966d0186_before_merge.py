def batch_fetch_art(lib, albums, force, maxwidth=None):
    """Fetch album art for each of the albums. This implements the manual
    fetchart CLI command.
    """
    for album in albums:
        if album.artpath and not force:
            message = 'has album art'
        else:
            # In ordinary invocations, look for images on the
            # filesystem. When forcing, however, always go to the Web
            # sources.
            local_paths = None if force else [album.path]

            path = art_for_album(album, local_paths, maxwidth)
            if path:
                album.set_art(path, False)
                album.store()
                message = 'found album art'
                if config['color']:
                    message = ui.colorize('red', message)
            else:
                message = 'no art found'
                if config['color']:
                    message = ui.colorize('turquoise', message)

        log.info(u'{0} - {1}: {2}'.format(album.albumartist, album.album,
                                          message))