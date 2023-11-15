    def _get_series_episodes(self, task, config, series_name, series_url, series_info):
        log.info('Retrieving new episodes for %s', series_name)
        response = requests.get(series_url + '/search?media_type=broadcast')  # only shows full episodes
        page = get_soup(response.content)

        if page.find('div', class_='npo3-show-items'):
            log.debug('Parsing as npo3')
            entries = self._parse_episodes_npo3(task, config, series_name, page, series_info)
        else:
            log.debug('Parsing as std')
            entries = self._parse_episodes_std(task, config, series_name, page, series_info)

        if not entries:
            log.warning('No episodes found for %s', series_name)

        return entries