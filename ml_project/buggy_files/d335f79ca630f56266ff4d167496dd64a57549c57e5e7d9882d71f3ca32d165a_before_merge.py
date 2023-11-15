    def fetch_popular_shows(self, page_url=None, trakt_list=None):
        """Get a list of popular shows from different Trakt lists based on a provided trakt_list.

        :param page_url: the page url opened to the base api url, for retreiving a specific list
        :param trakt_list: a description of the trakt list
        :return: A list of RecommendedShow objects, an empty list of none returned
        :throw: ``Exception`` if an Exception is thrown not handled by the libtrats exceptions
        """
        trending_shows = []
        removed_from_medusa = []

        # Create a trakt settings dict
        trakt_settings = {'trakt_api_secret': app.TRAKT_API_SECRET,
                          'trakt_api_key': app.TRAKT_API_KEY,
                          'trakt_access_token': app.TRAKT_ACCESS_TOKEN,
                          'trakt_refresh_token': app.TRAKT_REFRESH_TOKEN}

        trakt_api = TraktApi(timeout=app.TRAKT_TIMEOUT, ssl_verify=app.SSL_VERIFY, **trakt_settings)

        try:
            not_liked_show = ''
            if app.TRAKT_ACCESS_TOKEN != '':
                library_shows = self.fetch_and_refresh_token(trakt_api, 'sync/watched/shows?extended=noseasons') + \
                    self.fetch_and_refresh_token(trakt_api, 'sync/collection/shows?extended=full')

                medusa_shows = [show.indexerid for show in app.showList if show.indexerid]
                removed_from_medusa = [lshow['show']['ids']['tvdb'] for lshow in library_shows if lshow['show']['ids']['tvdb'] not in medusa_shows]

                if app.TRAKT_BLACKLIST_NAME is not None and app.TRAKT_BLACKLIST_NAME:
                    not_liked_show = trakt_api.request('users/' + app.TRAKT_USERNAME + '/lists/' +
                                                       app.TRAKT_BLACKLIST_NAME + '/items') or []
                else:
                    log.debug('Trakt blacklist name is empty')

            if trakt_list not in ['recommended', 'newshow', 'newseason']:
                limit_show = '?limit=' + text_type(100 + len(not_liked_show)) + '&'
            else:
                limit_show = '?'

            series = self.fetch_and_refresh_token(trakt_api, page_url + limit_show + 'extended=full,images') or []

            # Let's trigger a cache cleanup.
            missing_posters.clean()

            for show in series:
                try:
                    if 'show' not in show:
                        show['show'] = show

                    if not_liked_show and show['show']['ids']['tvdb'] in (s['show']['ids']['tvdb']
                                                                          for s in not_liked_show if s['type'] == 'show'):
                        continue

                    trending_shows.append(self._create_recommended_show(
                        show, storage_key='trakt_{0}'.format(show['show']['ids']['trakt'])
                    ))

                except MultipleShowObjectsException:
                    continue

            # Update the dogpile index. This will allow us to retrieve all stored dogpile shows from the dbm.
            blacklist = app.TRAKT_BLACKLIST_NAME not in ''

        except TraktException as error:
            log.warning('Could not connect to Trakt service: {0}', error)
            raise

        return blacklist, trending_shows, removed_from_medusa