def _chromium_version():
    """Get the Chromium version for QtWebEngine.

    This can also be checked by looking at this file with the right Qt tag:
    https://github.com/qt/qtwebengine/blob/dev/tools/scripts/version_resolver.py#L41

    Quick reference:
    Qt 5.7:  Chromium 49
    Qt 5.8:  Chromium 53
    Qt 5.9:  Chromium 56
    Qt 5.10: Chromium 61
    Qt 5.11: Chromium 63
    Qt 5.12: Chromium 65 (?)
    """
    if QWebEngineProfile is None:
        # This should never happen
        return 'unavailable'
    profile = QWebEngineProfile()
    ua = profile.httpUserAgent()
    match = re.search(r' Chrome/([^ ]*) ', ua)
    if not match:
        log.misc.error("Could not get Chromium version from: {}".format(ua))
        return 'unknown'
    return match.group(1)