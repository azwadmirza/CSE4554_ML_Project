    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        try:
            initial_data = data.get('Fs', [dict()])[0].get('Cn', {})
            torrent_rows = initial_data.get('torrents', []) if initial_data else None
        except (AttributeError, TypeError, KeyError, ValueError, IndexError) as error:
            # If TorrentDay changes their website issue will be opened so we can fix fast
            # and not wait user notice it's not downloading torrents from there
            log.error('TorrentDay response: {0}. Error: {1!r}', data, error)
            torrent_rows = None

        if not torrent_rows:
            log.debug('Data returned from provider does not contain any torrents')
            return items

        for row in torrent_rows:
            try:
                title = re.sub(r'\[.*=.*\].*\[/.*\]', '', row['name']) if row['name'] else None
                download_url = urljoin(self.urls['download'], '{}/{}'
                                       .format(row['id'], row['fname'])) if row['id'] and row['fname'] else None
                if not all([title, download_url]):
                    continue

                seeders = int(row['seed']) if row['seed'] else 1
                leechers = int(row['leech']) if row['leech'] else 0

                # Filter unseeded torrent
                if seeders < min(self.minseed, 1):
                    if mode != 'RSS':
                        log.debug("Discarding torrent because it doesn't meet the"
                                  " minimum seeders: {0}. Seeders: {1}",
                                  title, seeders)
                    continue

                torrent_size = row['size']
                size = convert_size(torrent_size) or -1
                pubdate_raw = row['added']
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