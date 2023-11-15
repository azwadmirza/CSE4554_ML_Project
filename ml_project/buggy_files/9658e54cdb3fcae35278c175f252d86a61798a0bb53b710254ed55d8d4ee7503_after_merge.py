    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html.parser') as html:  # Use html.parser, since html5parser has issues with this site.
            tables = html('table', width='750')  # Get the last table with a width of 750px.
            torrent_table = tables[-1] if tables else []
            torrent_rows = torrent_table('tr') if torrent_table else []

            # Continue only if at least one release is found
            if len(torrent_rows) < 2:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            # Skip column headers
            for row in torrent_rows[1:]:
                cells = row('td')
                if len(cells) < 3:
                    # We must have cells[2] because it containts the title
                    continue

                if self.freeleech and not row.get('bgcolor'):
                    continue

                try:
                    title = cells[2].find('a')['title'] if cells[2] else None
                    download_url = urljoin(self.url, cells[0].find('a')['href']) if cells[0] else None
                    if not all([title, download_url]):
                        continue

                    seeders = try_int(cells[8].get_text(strip=True)) if len(cells) > 8 else 1
                    leechers = try_int(cells[9].get_text(strip=True)) if len(cells) > 9 else 0

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    torrent_size = cells[6].get_text(' ') if len(cells) > 6 else None
                    size = convert_size(torrent_size) or -1

                    pubdate_raw = cells[5].get_text(" ")
                    pubdate = self._parse_pubdate(pubdate_raw)

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