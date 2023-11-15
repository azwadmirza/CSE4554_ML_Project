    def parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A list of items found
        """
        items = []

        with BS4Parser(data, 'html5lib') as html:
            torrent_table = html.find('table', border='1')
            torrent_rows = torrent_table('tr') if torrent_table else []

            # Continue only if at least one release is found
            if len(torrent_rows) < 2:
                log.debug('Data returned from provider does not contain any torrents')
                return items

            # "Type", "Name", Files", "Comm.", "Added", "TTL", "Size", "Snatched", "Seeders", "Leechers"
            labels = [label.get_text(strip=True) for label in torrent_rows[0]('td')]

            # Skip column headers
            for row in torrent_rows[1:]:
                cells = row('td')

                if len(cells) < len(labels):
                    continue

                try:
                    download_url = urljoin(self.url, cells[labels.index('Name')].find('a',
                                           href=re.compile(r'download.php\?id='))['href'])
                    title_element = cells[labels.index('Name')].find('a', href=re.compile(r'details.php\?id='))
                    title = title_element.get('title', '') or title_element.get_text(strip=True)
                    if not all([title, download_url]):
                        continue

                    # Free leech torrents are marked with green [F L] in the title
                    # (i.e. <font color=green>[F&nbsp;L]</font>)
                    freeleech = cells[labels.index('Name')].find('font', color='green')
                    if freeleech:
                        # \xa0 is a non-breaking space in Latin1 (ISO 8859-1)
                        freeleech_tag = '[F\xa0L]'
                        title = title.replace(freeleech_tag, '')
                        if self.freeleech and freeleech.get_text(strip=True) != freeleech_tag:
                            continue

                    seeders = try_int(cells[labels.index('Seeders')].get_text(strip=True), 1)
                    leechers = try_int(cells[labels.index('Leechers')].get_text(strip=True))

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            log.debug("Discarding torrent because it doesn't meet the"
                                      " minimum seeders: {0}. Seeders: {1}",
                                      title, seeders)
                        continue

                    torrent_size = cells[labels.index('Size')].get_text(' ', strip=True)
                    size = convert_size(torrent_size) or -1

                    pubdate_raw = cells[labels.index('Added')].get_text(' ', strip=True)
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