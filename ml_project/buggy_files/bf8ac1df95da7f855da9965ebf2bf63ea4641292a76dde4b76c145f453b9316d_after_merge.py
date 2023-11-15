    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        def process_column_header(th):
            return th.span.get_text() if th.span else th.get_text()

        with BS4Parser(data, 'html5lib') as html:
            torrent_table = html.find('table', class_='table2')

            if not torrent_table:
                logger.log('Data returned from provider does not contain any {0}torrents'.format(
                           'confirmed ' if self.confirmed else ''), logger.DEBUG)
                return items

            torrent_rows = torrent_table.find_all('tr')
            labels = [process_column_header(label) for label in torrent_rows[0]]

            # Skip the first row, since it isn't a valid result
            for row in torrent_rows[1:]:
                cells = row.find_all('td')

                try:
                    title_cell = cells[labels.index('Torrent Name')]

                    verified = title_cell.find('img', title='Verified torrent')
                    if self.confirmed and not verified:
                        continue

                    title_anchors = title_cell.find_all('a')
                    if not title_anchors or len(title_anchors) < 2:
                        continue

                    title_url = title_anchors[0].get('href')
                    title = title_anchors[1].get_text(strip=True)
                    regex_result = id_regex.search(title_anchors[1].get('href'))

                    alt_title = regex_result.group(1)
                    if len(title) < len(alt_title):
                        title = alt_title.replace('-', ' ')

                    torrent_id = regex_result.group(2)
                    torrent_hash = hash_regex.search(title_url).group(2)
                    if not all([title, torrent_id, torrent_hash]):
                        continue

                    with suppress(RequestsConnectionError, Timeout):
                        # Suppress the timeout since we are not interested in actually getting the results
                        self.session.get(self.urls['update'], timeout=0.1, params={'torrent_id': torrent_id,
                                                                                   'infohash': torrent_hash})

                    # Remove comma as thousands separator from larger number like 2,000 seeders = 2000
                    seeders = try_int(cells[labels.index('Seed')].get_text(strip=True).replace(',', ''), 1)
                    leechers = try_int(cells[labels.index('Leech')].get_text(strip=True).replace(',', ''))

                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            logger.log("Discarding torrent because it doesn't meet the "
                                       "minimum seeders: {0}. Seeders: {1}".format
                                       (title, seeders), logger.DEBUG)
                        continue

                    size = convert_size(cells[labels.index('Size')].get_text(strip=True)) or -1
                    download_url = 'magnet:?xt=urn:btih:{hash}&dn={title}{trackers}'.format(
                        hash=torrent_hash, title=title, trackers=self._custom_trackers)

                    item = {
                        'title': title,
                        'link': download_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers,
                        'pubdate': None,
                        'torrent_hash': torrent_hash,
                    }
                    if mode != 'RSS':
                        logger.log('Found result: {0} with {1} seeders and {2} leechers'.format
                                   (title, seeders, leechers), logger.DEBUG)

                    items.append(item)
                except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                    logger.log('Failed parsing provider. Traceback: {0!r}'.format
                               (traceback.format_exc()), logger.ERROR)

        return items