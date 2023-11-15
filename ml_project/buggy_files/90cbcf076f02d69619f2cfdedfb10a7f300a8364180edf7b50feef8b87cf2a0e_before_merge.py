    def fetch_popular_shows(self, page_url=None, trakt_list=None):  # pylint: disable=too-many-nested-blocks,too-many-branches
        """Get a list of popular shows from different Trakt lists based on a provided trakt_list.

        :param page_url: the page url opened to the base api url, for retreiving a specific list
        :param trakt_list: a description of the trakt list
        :return: A list of RecommendedShow objects, an empty list of none returned
        :throw: ``Exception`` if an Exception is thrown not handled by the libtrats exceptions
        """
        trending_shows = []
        blacklist = ''

        # Create a trakt settings dict
        trakt_settings = {'trakt_api_secret': sickbeard.TRAKT_API_SECRET, 'trakt_api_key': sickbeard.TRAKT_API_KEY,
                          'trakt_access_token': sickbeard.TRAKT_ACCESS_TOKEN}

        trakt_api = TraktApi(timeout=sickbeard.TRAKT_TIMEOUT, ssl_verify=sickbeard.SSL_VERIFY, **trakt_settings)

        try:  # pylint: disable=too-many-nested-blocks
            not_liked_show = ''
            if sickbeard.TRAKT_ACCESS_TOKEN != '':
                library_shows = self.fetch_and_refresh_token(trakt_api, 'sync/collection/shows?extended=full')

                if sickbeard.TRAKT_BLACKLIST_NAME is not None and sickbeard.TRAKT_BLACKLIST_NAME:
                    not_liked_show = trakt_api.request('users/' + sickbeard.TRAKT_USERNAME + '/lists/' +
                                                       sickbeard.TRAKT_BLACKLIST_NAME + '/items') or []
                else:
                    logger.log('Trakt blacklist name is empty', logger.DEBUG)

            if trakt_list not in ['recommended', 'newshow', 'newseason']:
                limit_show = '?limit=' + str(100 + len(not_liked_show)) + '&'
            else:
                limit_show = '?'

            shows = self.fetch_and_refresh_token(trakt_api, page_url + limit_show + 'extended=full,images') or []

            if sickbeard.TRAKT_ACCESS_TOKEN != '':
                library_shows = self.fetch_and_refresh_token(trakt_api, 'sync/collection/shows?extended=full') or []

            for show in shows:
                try:
                    if 'show' not in show:
                        show['show'] = show

                    if sickbeard.TRAKT_ACCESS_TOKEN != '':
                        if show['show']['ids']['tvdb'] not in (lshow['show']['ids']['tvdb']
                                                               for lshow in library_shows):
                            if not_liked_show:
                                if show['show']['ids']['tvdb'] not in (show['show']['ids']['tvdb']
                                                                       for show in not_liked_show if show['type'] == 'show'):
                                    trending_shows.append(self._create_recommended_show(show))
                            else:
                                trending_shows.append(self._create_recommended_show(show))
                    else:
                        if not_liked_show:
                            if show['show']['ids']['tvdb'] not in (show['show']['ids']['tvdb']
                                                                   for show in not_liked_show if show['type'] == 'show'):
                                trending_shows.append(self._create_recommended_show(show))
                        else:
                            trending_shows.append(self._create_recommended_show(show))

                except MultipleShowObjectsException:
                    continue

            blacklist = sickbeard.TRAKT_BLACKLIST_NAME not in ''

        except TraktException as e:
            logger.log('Could not connect to Trakt service: %s' % ex(e), logger.WARNING)
            raise

        return (blacklist, trending_shows)