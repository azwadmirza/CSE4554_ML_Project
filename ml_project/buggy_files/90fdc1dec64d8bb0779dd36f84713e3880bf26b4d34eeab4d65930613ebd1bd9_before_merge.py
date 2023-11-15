def url_get(base_url, password_mgr=None, pathspec=None, params=None):
    """Make contact with the uri provided and return any contents."""
    # Uses system proxy settings if they exist.
    proxy = urlrequest.ProxyHandler()
    if password_mgr is not None:
        auth = urlrequest.HTTPDigestAuthHandler(password_mgr)
        urlopener = urlrequest.build_opener(proxy, auth)
    else:
        urlopener = urlrequest.build_opener(proxy)
    urlrequest.install_opener(urlopener)
    full_url = build_url(base_url, pathspec=pathspec, params=params)
    response = urlopener.open(full_url)
    content = response.read()
    response.close()
    return content