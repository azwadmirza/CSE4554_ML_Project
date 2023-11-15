    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_rows = html.find('div', id='torrenttable').find_all('tr')

            # Continue only if at least one release is found
            if len(torrent_rows) < 2:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            # Scenetime apparently uses different number of cells in #torrenttable based
            # on who you are. This works around that by extracting labels from the first
            # <tr> and using their index to find the correct download/seeders/leechers td.
            labels = [label.get_text(strip=True) or label.img['title'] for label in torrent_rows[0]('td')]

            # Skip column headers
            for row in torrent_rows[1:]:
                cells = row('td')
                if len(cells) < len(labels):
                    continue

                try:
                    link = cells[labels.index('Name')]
                    torrent_id = link.find('a')['href'].replace('details.php?id=', '').split('&')[0]
                    title = link.find('a').get_text(strip=True)
                    download_url = self.urls['download'].format(
                        torrent_id,
                        '{0}.torrent'.format(title.replace(' ', '.'))
                    )
                    if not all([title, download_url]):
                        continue

                    seeders = try_int(cells[labels.index('Seeders')].get_text(strip=True))
                    leechers = try_int(cells[labels.index('Leechers')].get_text(strip=True))

                    # Filter unseeded torrent
                    if seeders < self.minseed:
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      ' minimum seeders: {0}. Seeders: {1}',
                                      title, seeders)
                        continue

                    torrent_size = cells[labels.index('Size')].get_text()
                    torrent_size = re.sub(r'(\d+\.?\d*)', r'\1 ', torrent_size)
                    size = convert_size(torrent_size) or -1

                    # Get the last item from the "span" list to avoid parsing "NEW!" as a pub date.
                    pubdate_raw = link.find_all('span')[-1]['title']
                    pubdate = self.parse_pubdate(pubdate_raw)

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
                    log.exception('Failed parsing provider.')

        return items