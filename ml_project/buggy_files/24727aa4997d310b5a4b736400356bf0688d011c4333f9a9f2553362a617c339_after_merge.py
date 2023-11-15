def request_defaults(kwargs):
    hooks = kwargs.pop(u'hooks', None)
    cookies = kwargs.pop(u'cookies', None)
    verify = certifi.old_where() if all([app.SSL_VERIFY, kwargs.pop(u'verify', True)]) else False

    # Fixes
    # https://github.com/pyca/pyopenssl/pull/209
    # https://github.com/pymedusa/Medusa/issues/1422
    if PY2 and isinstance(verify, text_type):
        verify = filesystem.encode(verify)

    # request session proxies
    if app.PROXY_SETTING:
        logger.debug(u"Using global proxy: " + app.PROXY_SETTING)
        scheme, address = splittype(app.PROXY_SETTING)
        address = app.PROXY_SETTING if scheme else 'http://' + app.PROXY_SETTING
        proxies = {
            "http": address,
            "https": address,
        }
    else:
        proxies = None

    return hooks, cookies, verify, proxies