    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:

            torrent_rows = html('div', class_='release_block')
            if len(torrent_rows) < 2:
                return items

            for row in torrent_rows[1:]:

                try:
                    first_cell = row.find('div', class_='release_row_first')
                    cells = row('div', class_='release_row')

                    title = cells[1].find('div', class_='release_text_contents').get_text().strip()
                    download_url = first_cell('a')[-1].get('href')

                    if not all([title, download_url]):
                        continue

                    download_url = urljoin(self.url, download_url)

                    # Provider does not support seeders or leechers.
                    seeders = -1
                    leechers = -1

                    torrent_size = first_cell.find('div', class_='release_size').get_text()
                    match_size = ShanaProjectProvider.size_regex.match(torrent_size)
                    try:
                        size = convert_size(match_size.group(1) + ' ' + match_size.group(2)) or -1
                    except AttributeError:
                        size = -1

                    date = cells[0].find('div', class_='release_last').get_text()
                    pubdate = parser.parse(date)

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