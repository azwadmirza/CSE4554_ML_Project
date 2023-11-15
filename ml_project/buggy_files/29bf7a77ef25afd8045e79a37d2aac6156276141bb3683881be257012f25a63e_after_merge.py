    def get_url_hook(response, **kwargs):
        """Get URL hook."""
        request = response.request
        log.debug('{0} URL: {1} [Status: {2}]', request.method, request.url, response.status_code)

        if request.method == 'POST':
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