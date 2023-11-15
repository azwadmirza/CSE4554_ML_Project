    def update_library(self, show=None):
        """Handles updating the Emby Media Server host via HTTP API

        Returns:
            Returns True for no issue or False if there was an error

        """

        if settings.USE_EMBY:
            if not settings.EMBY_HOST:
                logger.debug('EMBY: No host specified, check your settings')
                return False

            params = {}
            if show:
                params.update({
                    'Updates': [{
                        'Path': show.location,
                        'UpdateType': "Created"
                    }]
                })
                url = urljoin(settings.EMBY_HOST, 'emby/Library/Media/Updated')
            else:
                url = urljoin(settings.EMBY_HOST, 'emby/Library/Refresh')

            try:
                session = self.__make_session()
                response = session.post(url, json=params)
                response.raise_for_status()
                logger.debug('EMBY: HTTP response: {0}'.format(response.text.replace('\n', '')))
                return True

            except requests.exceptions.RequestException as error:
                logger.warning(f"EMBY: Warning: Could not contact Emby at {url} {error}")

                return False