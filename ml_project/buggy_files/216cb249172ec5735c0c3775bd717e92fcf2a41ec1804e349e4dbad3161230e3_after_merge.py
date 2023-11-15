def art_for_album(album, paths, maxwidth=None, local_only=False):
    """Given an Album object, returns a path to downloaded art for the
    album (or None if no art is found). If `maxwidth`, then images are
    resized to this maximum pixel size. If `local_only`, then only local
    image files from the filesystem are returned; no network requests
    are made.
    """
    out = None

    # Local art.
    cover_names = config['fetchart']['cover_names'].as_str_seq()
    cover_names = map(util.bytestring_path, cover_names)
    cautious = config['fetchart']['cautious'].get(bool)
    if paths:
        for path in paths:
            out = art_in_path(path, cover_names, cautious)
            if out:
                break

    # Web art sources.
    remote_priority = config['fetchart']['remote_priority'].get(bool)
    if not local_only and (remote_priority or not out):
        for url in _source_urls(album):
            if maxwidth:
                url = ArtResizer.shared.proxy_url(maxwidth, url)
            candidate = _fetch_image(url)
            if candidate:
                out = candidate
                break

    if maxwidth and out:
        out = ArtResizer.shared.resize(maxwidth, out)
    return out