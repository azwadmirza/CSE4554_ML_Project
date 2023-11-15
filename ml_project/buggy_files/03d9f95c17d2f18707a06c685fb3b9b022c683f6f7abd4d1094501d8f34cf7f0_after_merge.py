    def _get_series_episodes(self, task, config, series_name, series_url):
        log.info('Retrieving new episodes for %s', series_name)
        try:
            response = requests.get(series_url)
            page = get_soup(response.content)

            series_info = self._parse_series_info(task, config, page, series_url)
            episodes = page.find('div', id='component-grid-episodes')
            entries = self._parse_tiles(task, config, episodes, series_info)

            if not entries:
                log.warning('No episodes found for %s', series_name)

            return entries
        except RequestException as e:
            raise plugin.PluginError('Request error: %s' % e.args[0])