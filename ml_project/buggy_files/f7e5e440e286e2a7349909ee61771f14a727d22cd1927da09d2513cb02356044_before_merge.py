def download_url_to_fn(url, fn, on_error=None, max_retries=2, backoff_factor=0.5):
    """Download a URL to the given filename"""
    logger.info('Downloading %s to %s', url, fn)
    import requests
    from urllib3.util.retry import Retry
    from requests.adapters import HTTPAdapter
    session = requests.Session()
    # 408: request timeout
    # 429: too many requests
    # 500: internal server error
    # 502: bad gateway
    # 503: service unavailable
    # 504: gateway_timeout
    status_forcelist = (408, 429, 500, 502, 503, 504)
    # sourceforge.net directories to download mirror
    retries = Retry(total=max_retries, backoff_factor=backoff_factor,
                    status_forcelist=status_forcelist, redirect=5)
    session.mount('http://', HTTPAdapter(max_retries=retries))
    msg = _('Downloading url failed: %s') % url

    from bleachbit.Update import user_agent
    headers = {'user_agent': user_agent()}

    def do_error(msg2):
        if on_error:
            on_error(msg, msg2)
        from bleachbit.FileUtilities import delete
        delete(fn, ignore_missing=True)  # delete any partial download
    try:
        response = session.get(url, headers=headers)
        content = response.content
    except requests.exceptions.RequestException as exc:
        msg2 = '{}: {}'.format(type(exc).__name__, exc)
        logger.exception(msg)
        do_error(msg2)
        return False
    else:
        if not response.status_code == 200:
            logger.error(msg)
            msg2 = 'Status code: %s' % response.status_code
            do_error(msg2)
            return False

    with open(fn, 'wb') as f:
        f.write(content)
    return True