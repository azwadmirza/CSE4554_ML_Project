    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            if not html:
                log.debug('No html data parsed from provider')
                return items

            torrents = html('tr')
            if not torrents or len(torrents) < 2:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            # Skip column headers
            for row in torrents[1:]:
                # Skip extraneous rows at the end
                if len(row.contents) < 10:
                    continue

                try:
                    comments_counter = row.find_all('td', class_='lista', attrs={'align': 'center'})[4].find('a')
                    if comments_counter:
                        title = comments_counter['title'][10:]
                    else:
                        title = row.find('td', class_='lista', attrs={'align': 'left'}).find('a').get_text()
                    dl_href = row.find('td', class_='lista', attrs={'width': '20',
                                                                    'style': 'text-align: center;'}).find('a').get('href')
                    download_url = urljoin(self.url, dl_href)
                    if not all([title, dl_href]):
                        continue

                    seeders = try_int(row.find('span', class_='seedy').find('a').get_text(), 1)
                    leechers = try_int(row.find('span', class_='leechy').find('a').get_text())

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      ' minimum seeders: {0}. Seeders: {1}',
                                      title, seeders)
                        continue

                    torrent_size = row.find('td', class_='lista222', attrs={'width': '100%'}).get_text()
                    size = convert_size(torrent_size) or -1

                    pubdate_raw = row.find_all('td', class_='lista', attrs={'align': 'center'})[3].get_text()
                    pubdate = self.parse_pubdate(pubdate_raw)

                    item = {
                        'title': title,
                        'link': download_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers,
                        'pubdate': pubdate,
                    }
                    log.debug('Found result: {0} with {1} seeders and {2} leechers',
                              title, seeders, leechers)

                    items.append(item)
                except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                    log.exception('Failed parsing provider.')

        return items