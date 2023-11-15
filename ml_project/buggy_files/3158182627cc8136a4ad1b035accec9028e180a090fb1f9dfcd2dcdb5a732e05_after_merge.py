    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_table = html.find('div', class_='panel-body')
            torrent_rows = torrent_table('tr') if torrent_table else []

            # Continue only if at least one release is found
            if len(torrent_rows) < 2:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            # Skip column headers
            for row in torrent_rows[1:]:
                cells = row('td')

                try:
                    title = cells[1].find('a').get_text()
                    magnet = cells[2].find('a', title='Magnet link')['href']
                    download_url = '{magnet}{trackers}'.format(magnet=magnet,
                                                               trackers=self._custom_trackers)
                    if not all([title, download_url]):
                        continue

                    seeders = 1
                    leechers = 0
                    if len(cells) > 5:
                        peers = cells[5].find('div')
                        if peers and peers.get('title'):
                            peers = peers['title'].replace(',', '').split(' | ', 1)
                            # Removes 'Seeders: '
                            seeders = try_int(peers[0][9:])
                            # Removes 'Leechers: '
                            leechers = try_int(peers[1][10:])

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    torrent_size = cells[3].get_text().replace(',', '')
                    size = convert_size(torrent_size) or -1

                    pubdate_raw = cells[4].get_text().replace('yesterday', '24 hours')
                    # "long ago" can't be translated to a date
                    if pubdate_raw == 'long ago':
                        pubdate_raw = None
                    pubdate = self.parse_pubdate(pubdate_raw, human_time=True)

                    item = {
                        'title': title,
                        'link': download_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers,
                        'pubdate': pubdate,
                    }
                    if mode != 'RSS':
                        log.debug('Found result: {0} with {1} seeders and {2} leechers',
                                  title, seeders, leechers)

                    items.append(item)
                except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                    log.error('Failed parsing provider. Traceback: {0!r}',
                              traceback.format_exc())

        return items