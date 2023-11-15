    def _notify_emby(self, message, host=None, emby_apikey=None):
        """
        Notify Emby host via HTTP API.

        :return: True for no issue or False if there was an error
        """
        # fill in omitted parameters
        if not host:
            host = app.EMBY_HOST
        if not emby_apikey:
            emby_apikey = app.EMBY_APIKEY

        url = 'http://{host}/emby/Notifications/Admin'.format(host=host)
        data = json.dumps({
            'Name': 'Medusa',
            'Description': message,
            'ImageUrl': app.LOGO_URL
        })
        try:
            resp = self.session.post(
                url=url,
                data=data,
                headers={
                    'X-MediaBrowser-Token': emby_apikey,
                    'Content-Type': 'application/json'
                }
            )
            resp.raise_for_status()

            if resp.content:
                log.debug('EMBY: HTTP response: {0}', resp.content.replace('\n', ''))

            log.info('EMBY: Successfully sent a test notification.')
            return True

        except (HTTPError, RequestException) as error:
            log.warning('EMBY: Warning: Unable to contact Emby at {url}: {error}',
                        {'url': url, 'error': ex(error)})
            return False