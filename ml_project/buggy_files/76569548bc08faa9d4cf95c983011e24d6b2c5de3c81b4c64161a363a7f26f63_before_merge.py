    def _get_episodes(self, tvmaze_id, specials=False, aired_season=None):  # pylint: disable=unused-argument
        """
        Get all the episodes for a show by tvmaze id

        :param tvmaze_id: Series tvmaze id.
        :return: An ordered dict with the show searched for. In the format of OrderedDict{"episode": [list of episodes]}
        """
        # Parse episode data
        logger.debug('Getting all episodes of %s', [tvmaze_id])
        try:
            results = self.tvmaze_api.episode_list(tvmaze_id, specials=specials)
        except IDNotFound:
            logger.debug('Episode search did not return any results.')
            return False
        except BaseError as e:
            raise IndexerException('Show episodes search failed in getting a result with error: {0!r}'.format(e))

        episodes = self._map_results(results, self.series_map)

        if not episodes:
            return False

        if not isinstance(episodes, list):
            episodes = [episodes]

        for cur_ep in episodes:
            if self.config['dvdorder']:
                logger.debug('Using DVD ordering.')
                use_dvd = cur_ep['dvd_season'] is not None and cur_ep['dvd_episodenumber'] is not None
            else:
                use_dvd = False

            if use_dvd:
                seasnum, epno = cur_ep.get('dvd_season'), cur_ep.get('dvd_episodenumber')
            else:
                seasnum, epno = cur_ep.get('seasonnumber'), cur_ep.get('episodenumber')

            if seasnum is None or epno is None:
                logger.warning('An episode has incomplete season/episode number (season: %r, episode: %r)', seasnum, epno)
                continue  # Skip to next episode

            seas_no = int(seasnum)
            ep_no = int(epno)

            for k, v in cur_ep.items():
                k = k.lower()

                if v is not None:
                    if k == 'image_medium':
                        self._set_item(tvmaze_id, seas_no, ep_no, 'filename', v)
                self._set_item(tvmaze_id, seas_no, ep_no, k, v)