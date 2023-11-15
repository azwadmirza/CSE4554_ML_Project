    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            cls_name = 'search-ret' if mode != 'RSS' else 'recent'
            table_body = html.find('div', class_=cls_name)
            torrent_rows = table_body.find_all(
                'li', class_='{0}-item'.format(cls_name)
            ) if table_body else []

            # Continue only if at least one release is found
            if not table_body:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            for row in torrent_rows:
                try:

                    title = row.h2.find('a').get('title')
                    download_url = row.div.find('a').get('href')
                    if not all([title, download_url]):
                        continue

                    download_url += self._custom_trackers

                    spans = row.find('div').find_all('span')

                    seeders = int(spans[3].get_text().replace(',', ''))
                    leechers = int(spans[4].get_text().replace(',', ''))

                    torrent_size = spans[0].get_text()
                    size = convert_size(torrent_size, default=-1)

                    pubdate_raw = spans[2].get_text()
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