def fetch_url(url):
    """Retrieve the content at a given URL, or return None if the source
    is unreachable.
    """
    try:
        return urllib.urlopen(url).read()
    except IOError as exc:
        log.debug(u'failed to fetch: {0} ({1})'.format(url, unicode(exc)))
        return None