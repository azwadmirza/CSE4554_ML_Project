    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_table = html.find('table', {'id': 'torrent_table'})

            # Continue only if at least one release is found
            if not torrent_table:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            torrent_rows = torrent_table('tr', {'class': 'torrent'})

            # Continue only if one Release is found
            if not torrent_rows:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            for row in torrent_rows:
                try:
                    freeleech = row.find('img', alt='Freeleech') is not None
                    if self.freeleech and not freeleech:
                        continue

                    download_item = row.find('a', {'title': [
                        'Download Torrent',  # Download link
                        'Previously Grabbed Torrent File',  # Already Downloaded
                        'Currently Seeding Torrent',  # Seeding
                        'Currently Leeching Torrent',  # Leeching
                    ]})

                    if not download_item:
                        continue

                    download_url = urljoin(self.url, download_item['href'])

                    temp_anchor = row.find('a', {'data-src': True})
                    title = temp_anchor['data-src']
                    if not all([title, download_url]):
                        continue

                    cells = row('td')
                    seeders = try_int(cells[5].text.strip())
                    leechers = try_int(cells[6].text.strip())

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    size = temp_anchor['data-filesize'] or -1
                    pubdate_raw = cells[3].find('span')['title']
                    pubdate = parser.parse(pubdate_raw, fuzzy=True) if pubdate_raw else None

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