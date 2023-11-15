    def _get_favorites_entries(self, task, config, page):
        max_age = config.get('max_episode_age_days')
        if max_age >= 3:
            log.warning('If max_episode_age_days is 3 days or more, the plugin will still check all series')
        elif max_age > -1:
            return self._get_recent_entries(task, config, page)

        series = page.find('div', attrs={'id': 'component-grid-favourite-series'})

        entries = list()
        for list_item in series.findAll('div', class_='npo-ankeiler-tile-container'):
            url = list_item.find('a')['href']
            series_name = next(list_item.find('h2').stripped_strings)

            entries += self._get_series_episodes(task, config, series_name, url)

        return entries