    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_table = html('table', class_='table2')

            if mode != 'RSS' and torrent_table and len(torrent_table) < 2:
                logger.log('Data returned from provider does not contain any {0}torrents'.format(
                           'confirmed ' if self.confirmed else ''), logger.DEBUG)
                return items

            torrent_table = torrent_table[0 if mode == 'RSS' else 1]
            torrent_rows = torrent_table('tr')

            # Skip the first row, since it isn't a valid result
            for row in torrent_rows[1:]:
                cells = row('td')
                try:
                    verified = row('img', title='Verified torrent')
                    if self.confirmed and not verified:
                        continue

                    url = row.find('a', rel='nofollow')
                    title_info = row('a')
                    info = title_info[1]['href']
                    if not all([url, title_info, info]):
                        continue

                    title = title_info[1].get_text(strip=True)
                    title2 = id_regex.search(info).group(1)
                    if len(title) < len(title2):
                        title = title2.replace('-', ' ')
                    torrent_id = id_regex.search(info).group(2)
                    torrent_hash = hash_regex.search(url['href']).group(2)
                    if not all([title, torrent_id, torrent_hash]):
                        continue

                    with suppress(requests.exceptions.Timeout):
                        # Suppress the timeout since we are not interested in actually getting the results
                        self.session.get(self.urls['update'], timeout=0.1,
                                         params={'torrent_id': torrent_id,
                                                 'infohash': torrent_hash})

                    # Remove comma as thousands separator from larger number like 2,000 seeders = 2000
                    seeders = try_int(cells[3].get_text(strip=True).replace(',', ''))
                    leechers = try_int(cells[4].get_text(strip=True).replace(',', ''))
                    size = convert_size(cells[2].get_text(strip=True)) or -1
                    download_url = 'magnet:?xt=urn:btih:{hash}&dn={title}{trackers}'.format(
                        hash=torrent_hash, title=title, trackers=self._custom_trackers)

                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            logger.log("Discarding torrent because it doesn't meet the "
                                       "minimum seeders: {0}. Seeders: {1}".format
                                       (title, seeders), logger.DEBUG)
                        continue

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