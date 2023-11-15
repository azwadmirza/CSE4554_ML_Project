    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        torrent_rows = data

        for row in torrent_rows:
            try:
                title = torrent_rows[row]['release_name']
                download_url = torrent_rows[row]['download_url']
                if not all([title, download_url]):
                    continue

                seeders = torrent_rows[row]['seeders']
                leechers = torrent_rows[row]['leechers']

                # Filter unseeded torrent
                if seeders < min(self.minseed, 1):
                    if mode != 'RSS':
                        log.debug("Discarding torrent because it doesn't meet the"
                                  " minimum seeders: {0}. Seeders: {1}",
                                  title, seeders)
                    continue

                torrent_size = str(torrent_rows[row]['size']) + ' MB'
                size = convert_size(torrent_size) or -1

                pubdate_raw = torrent_rows[row]['added']
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