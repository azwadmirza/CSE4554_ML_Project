    def update_library(self, show=None):
        """
        Update the Emby Media Server host via HTTP API.

        :return: True for no issue or False if there was an error
        """
        if app.USE_EMBY:
            if not app.EMBY_HOST:
                log.debug('EMBY: No host specified, check your settings')
                return False

            if show:
                # EMBY only supports TVDB ids
                provider = 'tvdbid'
                if show.indexer == INDEXER_TVDBV2:
                    tvdb_id = show.indexerid
                else:
                    # Try using external ids to get a TVDB id
                    tvdb_id = show.externals.get(mappings[INDEXER_TVDBV2], None)

                if tvdb_id is None:
                    if show.indexer == INDEXER_TVRAGE:
                        log.warning('EMBY: TVRage indexer no longer valid')
                    else:
                        log.warning(
                            'EMBY: Unable to find a TVDB ID for {series},'
                            ' and {indexer} indexer is unsupported',
                            {'series': show.name, 'indexer': indexer_id_to_name(show.indexer)}
                        )
                    return False

                params = {
                    provider: text_type(tvdb_id)
                }
            else:
                params = {}

            url = 'http://{host}/emby/Library/Series/Updated'.format(host=app.EMBY_HOST)
            try:
                resp = self.session.post(
                    url=url,
                    params=params,
                    headers={
                        'X-MediaBrowser-Token': app.EMBY_APIKEY
                    }
                )
                resp.raise_for_status()

                if resp.content:
                    log.debug('EMBY: HTTP response: {0}', resp.content.replace('\n', ''))

                log.info('EMBY: Successfully sent a "Series Library Updated" command.')
                return True

            except (HTTPError, RequestException) as error:
                log.warning('EMBY: Warning: Unable to contact Emby at {url}: {error}',
                            {'url': url, 'error': ex(error)})
                return False