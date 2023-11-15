    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        # Units
        units = ['o', 'Ko', 'Mo', 'Go', 'To', 'Po']

        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_rows = html(class_=re.compile('ligne[01]'))
            for row in torrent_rows:
                try:
                    title = row.find(class_='titre').get_text(strip=True).replace('HDTV', 'HDTV x264-CPasBien')
                    title = re.sub(r' Saison', ' Season', title, flags=re.IGNORECASE)
                    tmp = row.find('a')['href'].split('/')[-1].replace('.html', '.torrent').strip()
                    download_url = (self.url + '/telechargement/%s' % tmp)
                    if not all([title, download_url]):
                        continue

                    seeders = try_int(row.find(class_='up').get_text(strip=True))
                    leechers = try_int(row.find(class_='down').get_text(strip=True))

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    torrent_size = row.find(class_='poid').get_text(strip=True)
                    size = convert_size(torrent_size, units=units) or -1

                    pubdate_raw = row.find('a')['title'].split("-")[1]
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