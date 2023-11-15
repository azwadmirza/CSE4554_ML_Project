    def _get_favorites_entries(self, task, config):
        email = config.get('email')
        max_age = config.get('max_episode_age_days')

        log.info('Retrieving npo.nl favorite series for %s', email)
        response = self._get_page(task, config, 'https://mijn.npo.nl/profiel/favorieten')
        page = get_soup(response.content)

        entries = list()
        for list_item in page.findAll('div', class_='thumb-item'):
            url = list_item.find('a')['href']

            if url == '/profiel/favorieten/favorieten-toevoegen':
                log.debug("Skipping 'add favorite' button")
                continue

            url = self._prefix_url('https://mijn.npo.nl', url)
            series_name = next(list_item.find('div', class_='thumb-item__title').stripped_strings)

            last_aired_text = list_item.find('div', class_='thumb-item__subtitle').text
            last_aired_text = last_aired_text.rsplit('Laatste aflevering ')[-1]
            last_aired = self._parse_date(last_aired_text)

            if last_aired is None:
                log.info('Series %s did not yet start', series_name)
                continue
            elif max_age >= 0 and (date.today() - last_aired) > timedelta(days=max_age):
                log.debug('Skipping %s, last aired on %s', series_name, last_aired)
                continue
            elif (date.today() - last_aired) > timedelta(days=365 * 2):
                log.info('Series %s last aired on %s', series_name, last_aired)

            series_info = self._get_series_info(task, config, series_name, url)

            entries += self._get_series_episodes(task, config, series_name, url, series_info)

        return entries