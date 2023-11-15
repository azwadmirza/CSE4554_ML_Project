    def _parse_episodes(self, tvdb_id, episode_data):
        """Parse retreived episodes."""
        if 'episode' not in episode_data:
            return False

        episodes = episode_data['episode']
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
                logger.warning('This episode has incomplete information. The season or episode number '
                               '(season: %s, episode: %s) is missing. '
                               'to get rid of this warning, you will have to contact tvdb through their forums '
                               'and have them fix the specific episode.',
                               seasnum, epno)
                continue  # Skip to next episode

            # float() is because https://github.com/dbr/tvnamer/issues/95 - should probably be fixed in TVDB data
            seas_no = int(float(seasnum))
            ep_no = int(float(epno))

            for k, v in cur_ep.items():
                k = k.lower()

                if v is not None:
                    if k == 'filename':
                        v = urljoin(self.config['artwork_prefix'], v)
                    else:
                        v = self._clean_data(v)

                self._set_item(tvdb_id, seas_no, ep_no, k, v)