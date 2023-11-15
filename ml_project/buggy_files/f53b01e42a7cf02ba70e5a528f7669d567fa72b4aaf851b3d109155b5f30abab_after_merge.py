def log_url(response, **kwargs):
    """Response hook to log request URL."""
    request = response.request
    log.debug(
        '{method} URL: {url} [Status: {status}]'.format(
            method=request.method,
            url=request.url,
            status=response.status_code,
        )
    )
    log.debug('User-Agent: {}'.format(request.headers['User-Agent']))

    if request.method.upper() == 'POST':
        body = request.body
        # try to log post data using various codecs to decode
        codecs = ('utf-8', 'latin1', 'cp1252')
        for codec in codecs:
            try:
                data = body.decode(codec)
            except UnicodeError as error:
                log.debug('Failed to decode post data as {codec}: {msg}',
                          codec=codec, msg=error)
            else:
                log.debug('With post data: {0}', data)
                break
        else:
            log.warning('Failed to decode post data with {codecs}',
                        codecs=codecs)