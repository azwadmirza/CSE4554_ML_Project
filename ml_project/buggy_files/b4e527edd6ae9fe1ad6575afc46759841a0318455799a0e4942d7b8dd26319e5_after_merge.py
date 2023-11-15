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
                log.debug('Data returned from provider does not contain any {0}torrents',
                          'ranked ' if self.ranked else '')
                return items

            torrent_body = torrent_table.find('tbody')
            torrent_rows = torrent_body.contents
            del torrent_rows[1::2]

            for row in torrent_rows[1:]:
                try:
                    torrent = row('td')
                    if len(torrent) <= 1:
                        break

                    all_as = (torrent[1])('a')
                    notinternal = row.find('img', src='/static//common/user_upload.png')
                    if self.ranked and notinternal:
                        log.debug('Found a user uploaded release, Ignoring it..')
                        continue

                    freeleech = row.find('img', src='/static//common/browse/freeleech.png')
                    if self.freeleech and not freeleech:
                        continue

                    title = all_as[2].string
                    download_url = urljoin(self.url, all_as[0].attrs['href'])
                    if not all([title, download_url]):
                        continue

                    seeders = try_int((row('td')[6]).text.replace(',', ''))
                    leechers = try_int((row('td')[7]).text.replace(',', ''))

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    torrent_size = row.find('td', class_='nobr').find_next_sibling('td').string
                    if torrent_size:
                        size = convert_size(torrent_size) or -1

                    pubdate_raw = row.find('td', class_='nobr').find('span')['title']
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