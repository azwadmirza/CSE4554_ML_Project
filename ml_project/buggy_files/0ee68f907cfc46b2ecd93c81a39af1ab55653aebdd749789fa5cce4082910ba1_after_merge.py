def fetch_url(url):
    """Retrieve the content at a given URL, or return None if the source
    is unreachable.
    """
    r = requests.get(url)
    if r.status_code == requests.codes.ok:
        return r.text
    else:
        log.debug(u'failed to fetch: {0} ({1})'.format(url, r.status_code))
    return None