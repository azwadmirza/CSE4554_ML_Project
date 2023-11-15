def log_url(resp, **kwargs):
    """Response hook to log request URL."""
    log.debug(
        '{method} URL: {url} [Status: {status}]'.format(
            method=resp.request.method,
            url=resp.request.url,
            status=resp.status_code,
        )
    )
    log.debug('User-Agent: {}'.format(resp.request.headers['User-Agent']))

    if resp.request.method.upper() == 'POST':
        data = resp.request.body.decode('utf-8')
        log.debug('With post data: {data}'.format(data=data))

    return resp