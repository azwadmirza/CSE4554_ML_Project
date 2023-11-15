    def _get_episodes(self, tmdb_id, specials=False, aired_season=None):  # pylint: disable=unused-argument
        """Get all the episodes for a show by tmdb id.

        :param tmdb_id: Series tmdb id.
        :return: An ordered dict with the show searched for. In the format of OrderedDict{"episode": [list of episodes]}
        """
        results = []
        if aired_season:
            aired_season = [aired_season] if not isinstance(aired_season, list) else aired_season
        else:
            if tmdb_id not in self.shows or not self.shows[tmdb_id].data.get('seasons'):
                self.config['episodes_enabled'] = False  # Don't want to get episodes, as where already doing that.
                self._get_show_data(tmdb_id)  # Get show data, with the list of seasons
            aired_season = [season['season_number'] for season in self.shows[tmdb_id].data.get('seasons', [])]

        if not aired_season:
            raise IndexerShowIncomplete('This show does not have any seasons on TMDB.')

        # Parse episode data
        logger.debug('Getting all episodes of %s', [tmdb_id])

        # get episodes for each season
        for season in aired_season:
            season_info = self.tmdb.TV_Seasons(tmdb_id, season).info(language=self.config['language'])
            results += season_info['episodes']

        if not results:
            logger.debug('Series results incomplete')
            raise IndexerShowIncomplete('Show search returned incomplete results '
                                        '(cannot find complete show on TheMovieDb)')

        mapped_episodes = self._map_results(results, self.episodes_map, '|')
        episode_data = OrderedDict({'episode': mapped_episodes})

        if 'episode' not in episode_data:
            return False

        episodes = episode_data['episode']
        if not isinstance(episodes, list):
            episodes = [episodes]

        for cur_ep in episodes:
            if self.config['dvdorder']:
                logger.debug('Using DVD ordering.')
                use_dvd = cur_ep.get('dvd_season') is not None and cur_ep.get('dvd_episodenumber') is not None
            else:
                use_dvd = False

            if use_dvd:
                seasnum, epno = cur_ep.get('dvd_season'), cur_ep.get('dvd_episodenumber')
            else:
                seasnum, epno = cur_ep.get('seasonnumber'), cur_ep.get('episodenumber')
                if self.config['dvdorder']:
                    logger.warning('Episode doest not have DVD ordering available (season: %s, episode: %s). '
                                   'Falling back to non-DVD order. '
                                   'Please consider disable DVD ordering for the show with TMDB ID: %s',
                                   seasnum, epno, tmdb_id)

            if seasnum is None or epno is None:
                logger.warning('An episode has incomplete season/episode number (season: %r, episode: %r)', seasnum, epno)
                continue  # Skip to next episode

            seas_no = int(seasnum)
            ep_no = int(epno)

            image_width = {'fanart': 'w1280', 'poster': 'w780', 'filename': 'w300'}
            for k, v in cur_ep.items():
                k = k.lower()

                if v is not None:
                    if k in ['filename', 'poster', 'fanart']:
                        # I'm using the default 'original' quality. But you could also check tmdb_configuration,
                        # for the available image sizes.
                        v = self.config['artwork_prefix'].format(base_url=self.tmdb_configuration.images['base_url'],
                                                                 image_size=image_width[k],
                                                                 file_path=v)
                self._set_item(tmdb_id, seas_no, ep_no, k, v)