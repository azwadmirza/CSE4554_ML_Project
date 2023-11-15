    def on_task_input(self, task, config):
        config = self.prepare_config(config)

        # Create movie entries by parsing imdb list page(s) html using beautifulsoup
        log.verbose('Retrieving imdb list: %s', config['list'])

        params = {'view': 'compact', 'start': 1}
        if config['list'] in ['watchlist', 'ratings', 'checkins']:
            url = 'http://www.imdb.com/user/%s/%s' % (config['user_id'], config['list'])
        else:
            url = 'http://www.imdb.com/list/%s' % config['list']

        headers = {'Accept-Language': config.get('force_language')}
        log.debug('Requesting: %s %s', url, headers)

        try:
            page = task.requests.get(url, params=params, headers=headers)
        except HTTPError as e:
            raise plugin.PluginError(e.args[0])
        if page.status_code != 200:
            raise plugin.PluginError('Unable to get imdb list. Either list is private or does not exist.')

        soup = get_soup(page.text)

        try:
            total_item_count = int(soup.find('div', class_='desc').get('data-size'))
            log.verbose('imdb list contains %s items', total_item_count)
        except AttributeError:
            total_item_count = 0
        except ValueError as e:
            # TODO Something is wrong if we get a ValueError, I think
            raise plugin.PluginError('Received invalid movie count: %s - %s' %
                                     (soup.find('div', class_='desc').get('data-size'), e))

        if total_item_count == 0:
            log.verbose('No movies were found in imdb list: %s', config['list'])
            return

        entries = []
        items_processed = 0
        while items_processed < total_item_count:
            # Fetch the next page unless we've just begun
            if items_processed:
                params['start'] = items_processed + 1
                page = task.requests.get(url, params=params)
                if page.status_code != 200:
                    raise plugin.PluginError('Unable to get imdb list.')
                soup = get_soup(page.text)

            items = soup.find_all(attrs={'data-item-id': True, 'class': 'list_item'})

            for item in items:
                items_processed += 1
                a = item.find('td', class_='title').find('a')
                if not a:
                    log.debug('no title link found for row, skipping')
                    continue

                title_type = item.find('td', class_='title_type').text.strip()
                if 'all' not in config['type'] and TITLE_TYPE_MAP.get(title_type) not in config['type']:
                    log.verbose('Skipping title %s since it is a %s', a.text,
                                TITLE_TYPE_MAP.get(title_type).rstrip('s'))
                    continue
                link = ('http://www.imdb.com' + a.get('href')).rstrip('/')
                entry = Entry()
                entry['title'] = a.text
                entry['imdb_type'] = title_type
                try:
                    year = int(item.find('td', class_='year').text)
                    entry['title'] += ' (%s)' % year
                    entry['imdb_year'] = year
                except ValueError:
                    pass
                entry['url'] = link
                entry['imdb_id'] = extract_id(link)
                entry['imdb_name'] = entry['title']
                entries.append(entry)

        return entries