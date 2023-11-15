    def get_items(self):
        """Iterator over etrieved itesms from the trakt api."""
        if self.config['list'] in ['collection', 'watched', 'trending', 'popular'] and self.config['type'] == 'auto':
            raise plugin.PluginError(
                '`type` cannot be `auto` for %s list.' % self.config['list']
            )

        limit_per_page = 1000

        endpoint = self.get_list_endpoint()

        list_type = (self.config['type']).rstrip('s')

        log.verbose('Retrieving `%s` list `%s`', self.config['type'], self.config['list'])
        try:
            page = 1
            collecting_finished = False
            while not collecting_finished:
                result = self.session.get(
                    db.get_api_url(endpoint), params={'limit': limit_per_page, 'page': page}
                )
                page = int(result.headers.get('X-Pagination-Page', 1))
                number_of_pages = int(result.headers.get('X-Pagination-Page-Count', 1))
                if page == 2:
                    # If there is more than one page (more than 1000 items) warn user they may want to limit
                    log.verbose('There are a large number of items in trakt `%s` list. You may want to enable `limit`'
                                ' plugin to reduce the amount of entries in this task.', self.config['list'])

                collecting_finished = page >= number_of_pages
                page += 1

                try:
                    trakt_items = result.json()
                except ValueError:
                    log.debug(
                        'Could not decode json from response: %s', result.text
                    )
                    raise plugin.PluginError('Error getting list from trakt.')
                if not trakt_items:
                    log.warning(
                        'No data returned from trakt for %s list %s.',
                        self.config['type'],
                        self.config['list'],
                    )
                    return

                for item in trakt_items:
                    if self.config['type'] == 'auto':
                        list_type = item['type']
                    if self.config['list'] == 'popular':
                        item = {list_type: item}
                    # Collection and watched lists don't return 'type' along with the items (right now)
                    if 'type' in item and item['type'] != list_type:
                        log.debug(
                            'Skipping %s because it is not a %s',
                            item[item['type']].get('title', 'unknown'),
                            list_type,
                        )
                        continue
                    if list_type != 'episode' and not item[list_type]['title']:
                        # Skip shows/movies with no title
                        log.warning('Item in trakt list does not appear to have a title, skipping.')
                        continue
                    entry = Entry()
                    if list_type == 'episode':
                        entry['url'] = 'https://trakt.tv/shows/%s/seasons/%s/episodes/%s' % (
                            item['show']['ids']['slug'],
                            item['episode']['season'],
                            item['episode']['number'],
                        )
                    else:
                        entry['url'] = 'https://trakt.tv/%ss/%s' % (
                            list_type,
                            item[list_type]['ids'].get('slug'),
                        )

                    # Pass the strip dates option in so it can be used in the update maps
                    item['strip_dates'] = self.config.get('strip_dates')
                    entry.update_using_map(field_maps[list_type], item)

                    # get movie name translation
                    language = self.config.get('language')
                    if list_type == 'movie' and language:
                        endpoint = ['movies', entry['trakt_movie_id'], 'translations', language]
                        try:
                            result = self.session.get(db.get_api_url(endpoint))
                            try:
                                translation = result.json()
                            except ValueError:
                                raise plugin.PluginError(
                                    'Error decoding movie translation from trakt: %s.' % result.text
                                )
                        except RequestException as e:
                            raise plugin.PluginError(
                                'Could not retrieve movie translation from trakt: %s' % str(e)
                            )
                        if not translation:
                            log.warning(
                                'No translation data returned from trakt for movie %s.', entry['title']
                            )
                        else:
                            log.verbose(
                                'Found `%s` translation for movie `%s`: %s',
                                language,
                                entry['movie_name'],
                                translation[0]['title'],
                            )
                            entry['title'] = translation[0]['title']
                            if entry.get('movie_year') and not self.config.get('strip_dates'):
                                entry['title'] += ' ({})'.format(entry['movie_year'])
                            entry['movie_name'] = translation[0]['title']

                    if entry.isvalid():
                        yield entry
                    else:
                        log.debug('Invalid entry created? %s', entry)

        except RequestException as e:
            raise plugin.PluginError('Could not retrieve list from trakt (%s)' % e)