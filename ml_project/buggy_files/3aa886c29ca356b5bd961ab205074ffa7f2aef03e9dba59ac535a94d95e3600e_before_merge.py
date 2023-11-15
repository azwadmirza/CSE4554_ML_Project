    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_rows = html('tr')

            if not torrent_rows or not len(torrent_rows) > 1:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            # Cat., Active, Filename, Dl, Wl, Added, Size, Uploader, S, L, C
            labels = [label.a.get_text(strip=True) if label.a else label.get_text(strip=True) for label in
                      torrent_rows[0]('th')]

            # Skip column headers
            for row in torrent_rows[1:]:
                try:
                    cells = row.find_all('td', recursive=False)[:len(labels)]
                    if len(cells) < len(labels):
                        continue

                    torrent_name = cells[labels.index('Torrent name')].a
                    title = torrent_name.get_text(strip=True) if torrent_name else None
                    download_url = torrent_name.get('href') if torrent_name else None
                    if not all([title, download_url]):
                        continue

                    slc = cells[labels.index('S')].get_text()
                    seeders, leechers, _ = [int(value.strip()) for value in slc.split('/')] if slc else (0, 0, 0)

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    torrent_size = cells[labels.index('Size')].get_text()
                    size = convert_size(torrent_size) or -1

                    pubdate_raw = cells[labels.index('Added')].get_text() if cells[labels.index('Added')] else None
                    pubdate = parser.parse(pubdate_raw) if pubdate_raw else None

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