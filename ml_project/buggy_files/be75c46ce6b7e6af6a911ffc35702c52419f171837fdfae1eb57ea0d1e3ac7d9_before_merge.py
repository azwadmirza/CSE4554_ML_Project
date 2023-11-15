    def _get_watchlist_entries(self, task, config):
        email = config.get('email')
        log.info('Retrieving npo.nl episode watchlist for %s', email)

        response = self._get_page(task, config, 'https://mijn.npo.nl/profiel/kijklijst')
        page = get_soup(response.content)

        self.csrf_token = page.find('meta', attrs={'name': 'csrf-token'})['content']

        entries = list()
        for list_item in page.findAll('div', class_='watch-list-item'):
            url = list_item.find('a')['href']
            series_name = next(list_item.find('h3').stripped_strings)
            remove_url = list_item.find('a', class_='unwatch-confirm')['href']
            entry_date = self._parse_date(list_item.find('span', class_='global__content-info').text)

            episode_id = url.split('/')[-1]
            title = '{} ({})'.format(series_name, episode_id)

            e = Entry()
            e['url'] = self._prefix_url('https://mijn.npo.nl', url)
            e['title'] = title
            e['series_name'] = series_name
            e['series_name_plain'] = self._convert_plain(series_name)
            e['series_date'] = entry_date
            e['series_id_type'] = 'date'
            e['description'] = list_item.find('p').text
            e['remove_url'] = self._prefix_url('https://mijn.npo.nl', remove_url)

            if config.get('remove_accepted'):
                e.on_complete(self.entry_complete, task=task)

            entries.append(e)

        return entries