def data_for_url(url):
    """Get the data to show for the given URL.

    Args:
        url: The QUrl to show.

    Return:
        A (mimetype, data) tuple.
    """
    norm_url = url.adjusted(QUrl.NormalizePathSegments |
            QUrl.StripTrailingSlash)
    if norm_url != url:
        raise Redirect(norm_url)

    path = url.path()
    host = url.host()
    query = urlutils.query_string(url)
    # A url like "qute:foo" is split as "scheme:path", not "scheme:host".
    log.misc.debug("url: {}, path: {}, host {}".format(
        url.toDisplayString(), path, host))
    if not path or not host:
        new_url = QUrl()
        new_url.setScheme('qute')
        # When path is absent, e.g. qute://help (with no trailing slash)
        if host:
            new_url.setHost(host)
        # When host is absent, e.g. qute:help
        else:
            new_url.setHost(path)

        new_url.setPath('/')
        if query:
            new_url.setQuery(query)
        if new_url.host():  # path was a valid host
            raise Redirect(new_url)

    try:
        handler = _HANDLERS[host]
    except KeyError:
        raise NoHandlerFound(url)

    try:
        mimetype, data = handler(url)
    except OSError as e:
        # FIXME:qtwebengine how to handle this?
        raise QuteSchemeOSError(e)
    except QuteSchemeError as e:
        raise

    assert mimetype is not None, url
    if mimetype == 'text/html' and isinstance(data, str):
        # We let handlers return HTML as text
        data = data.encode('utf-8', errors='xmlcharrefreplace')

    return mimetype, data