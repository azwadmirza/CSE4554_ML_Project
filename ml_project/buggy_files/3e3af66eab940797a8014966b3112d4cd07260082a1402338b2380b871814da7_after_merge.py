    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_rows = html('item')

            for row in torrent_rows:
                try:
                    if row.category and 'tv' not in row.category.get_text(strip=True).lower():
                        continue

                    title_raw = row.title.text
                    # Add "-" after codec and add missing "."
                    title = re.sub(r'([xh][ .]?264|xvid)( )', r'\1-', title_raw).replace(' ', '.') if title_raw else ''
                    info_hash = row.guid.text.rsplit('/', 1)[-1]
                    download_url = "magnet:?xt=urn:btih:" + info_hash + "&dn=" + title + self._custom_trackers
                    if not all([title, download_url]):
                        continue

                    torrent_size, seeders, leechers = self._split_description(row.find('description').text)
                    size = convert_size(torrent_size) or -1
                    pubdate_raw = row.pubDate.text if row.pubDate else None
                    pubdate = self._parse_pubdate(pubdate_raw)

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

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