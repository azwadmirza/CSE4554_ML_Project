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
                if show.indexer == 1:
                    provider = 'tvdb'
                elif show.indexer == 2:
                    logger.warning('EMBY: TVRage Provider no longer valid')
                    return False
                else:
                    logger.warning('EMBY: Provider unknown')
                    return False
                params.update({f'{provider}id': show.indexerid})

            url = urljoin(settings.EMBY_HOST, 'emby/Library/Series/Updated')

            try:
                session = self.__make_session()
                response = session.get(url, params=params)
                response.raise_for_status()
                logger.debug('EMBY: HTTP response: {0}'.format(response.text.replace('\n', '')))
                return True

            except requests.exceptions.RequestException as error:
                logger.warning(f"EMBY: Warning: Could not contact Emby at {url} {error}")

                return False