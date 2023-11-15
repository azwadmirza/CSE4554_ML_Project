    def _get_show_data(self, sid, language='en'):
        """Take a series ID, gets the epInfo URL and parses the TMDB json response.

        into the shows dict in layout:
        shows[series_id][season_number][episode_number]
        """
        if self.config['language'] is None:
            log.debug('Config language is none, using show language')
            if language is None:
                raise IndexerError("config['language'] was None, this should not happen")
            get_show_in_language = language
        else:
            log.debug('Configured language {0} override show language of {1}',
                      self.config['language'], language)
            get_show_in_language = self.config['language']

        # Parse show information
        log.debug('Getting all series data for {0}', sid)

        # Parse show information
        series_info = self._get_show_by_id(sid, request_language=get_show_in_language)

        if not series_info:
            log.debug('Series result returned zero')
            raise IndexerError('Series result returned zero')

        # get series data / add the base_url to the image urls
        # Create a key/value dict, to map the image type to a default image width.
        # possitlbe widths can also be retrieved from self.configuration.images['poster_sizes'] and
        # self.configuration.images['still_sizes']
        image_width = {'fanart': 'w1280', 'poster': 'w500'}

        for k, v in viewitems(series_info['series']):
            if v is not None:
                if k in ['fanart', 'banner', 'poster']:
                    v = self.config['artwork_prefix'].format(base_url=self.tmdb_configuration.images['base_url'],
                                                             image_size=image_width[k],
                                                             file_path=v)

            self._set_show_data(sid, k, v)

        # Get external ids.
        # As the external id's are not part of the shows default response, we need to make an additional call for it.
        self._set_show_data(sid, 'externals', self.tmdb.TV(sid).external_ids())

        # get episode data
        if self.config['episodes_enabled']:
            self._get_episodes(sid, specials=False, aired_season=None)

        # Parse banners
        if self.config['banners_enabled']:
            self._parse_images(sid)

        # Parse actors
        if self.config['actors_enabled']:
            self._parse_actors(sid)

        return True