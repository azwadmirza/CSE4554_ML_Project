    def _get_series_info(self, task, config, episode_name, episode_url):
        log.info('Retrieving series info for %s', episode_name)
        try:
            response = requests.get(episode_url)
            page = get_soup(response.content)

            series_url = page.find('a', class_='npo-episode-header-program-info')['href']

            if series_url not in self._series_info:
                response = requests.get(series_url)
                page = get_soup(response.content)

                series_info = self._parse_series_info(task, config, page, series_url)
                self._series_info[series_url] = series_info

            return self._series_info[series_url]
        except RequestException as e:
            raise plugin.PluginError('Request error: %s' % e.args[0])