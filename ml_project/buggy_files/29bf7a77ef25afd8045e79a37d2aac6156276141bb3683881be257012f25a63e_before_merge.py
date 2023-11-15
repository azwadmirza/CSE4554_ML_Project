    def get_url_hook(response, **kwargs):
        """Get URL hook."""
        log.debug('{0} URL: {1} [Status: {2}]', response.request.method, response.request.url, response.status_code)

        if response.request.method == 'POST':
            data = response.request.body.decode('utf-8')
            log.debug('With post data: {0}', data)