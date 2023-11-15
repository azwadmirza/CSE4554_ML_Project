    def _parse(self, data, mode):
        """
        Parse search results for items.

        :param data: The raw response from a search
        :param mode: The current mode used to search, e.g. RSS

        :return: A KV with a list of items found and if there's an next page to search
        """

        def process_column_header(td):
            ret = ''
            if td.a and td.a.img:
                ret = td.a.img.get('title', td.a.get_text(strip=True))
            if not ret:
                ret = td.get_text(strip=True)
            return ret

        items = []
        has_next_page = False
        with BS4Parser(data, 'html5lib') as html:
            torrent_table = html.find('table', id='torrent_table')
            torrent_rows = torrent_table('tr') if torrent_table else []

            # ignore next page in RSS mode
            has_next_page = mode != 'RSS' and html.find('a', class_='pager_next') is not None
            logger.log('More Pages? {0}'.format(has_next_page), logger.DEBUG)

            # Continue only if at least one Release is found
            if len(torrent_rows) < 2:
                logger.log('Data returned from provider does not contain any torrents', logger.DEBUG)
                return {'has_next_page': has_next_page, 'items': []}

            # '', '', 'Name /Year', 'Files', 'Time', 'Size', 'Snatches', 'Seeders', 'Leechers'
            labels = [process_column_header(label) for label in torrent_rows[0]('td')]
            group_title = ''

            # Skip column headers
            for result in torrent_rows[1:]:
                cells = result('td')
                result_class = result.get('class')
                # When "Grouping Torrents" is enabled, the structure of table change
                group_index = -2 if 'group_torrent' in result_class else 0
                try:
                    title = result.select('a[href^="torrents.php?id="]')[0].get_text()
                    title = re.sub('\s+', ' ', title).strip()  # clean empty lines and multiple spaces

                    if 'group' in result_class or 'torrent' in result_class:
                        # get international title if available
                        title = re.sub('.* \[(.*?)\](.*)', r'\1\2', title)

                    if 'group' in result_class:
                        group_title = title
                        continue

                    # Clean dash between title and season/episode
                    title = re.sub('- (S\d{2}(E\d{2,4})?)', r'\1', title)

                    for serie in self.absolute_numbering:
                        if serie in title:
                            # remove season from title when its in absolute format
                            title = re.sub('S\d{2}E(\d{2,4})', r'\1', title)
                            break

                    download_url = urljoin(self.url,
                                           result.select('a[href^="torrents.php?action=download"]')[0]['href'])
                    if not all([title, download_url]):
                        continue

                    # seeders = try_int(cells[labels.index('Seeders') + group_index].get_text(strip=True))
                    # leechers = try_int(cells[labels.index('Leechers') + group_index].get_text(strip=True))

                    seeders = try_int(cells[4].get_text(strip=True))
                    leechers = try_int(cells[5].get_text(strip=True))

                    # Filter unseeded torrent
                    if seeders < self.minseed or leechers < self.minleech:
                        if mode != "RSS":
                            logger.log("Discarding torrent because it doesn't meet the"
                                       " minimum seeders or leechers: {0} (S:{1} L:{2})".format
                                       (title, seeders, leechers), logger.DEBUG)
                        continue

                    torrent_details = None
                    if 'group_torrent' in result_class:
                        # torrents belonging to a group
                        torrent_details = title
                        title = group_title
                    elif 'torrent' in result_class:
                        # standalone/un grouped torrents
                        torrent_details = cells[labels.index('Nome/Ano')].find('div', class_='torrent_info').get_text()

                    torrent_details = torrent_details.replace('[', ' ').replace(']', ' ').replace('/', ' ')
                    torrent_details = torrent_details.replace('Full HD ', '1080p').replace('HD ', '720p')

                    # torrent_size = cells[labels.index('Tamanho') + group_index].get_text(strip=True)
                    torrent_size = cells[2].get_text(strip=True)

                    size = convert_size(torrent_size) or -1

                    torrent_name = '{0} {1}'.format(title, torrent_details.strip()).strip()
                    torrent_name = re.sub('\s+', ' ', torrent_name)

                    items.append({
                        'title': torrent_name,
                        'link': download_url,
                        'size': size,
                        'seeders': seeders,
                        'leechers': leechers,
                        'hash': ''
                    })

                    if mode != 'RSS':
                        logger.log('Found result: {0} with {1} seeders and {2} leechers'.format
                                   (torrent_name, seeders, leechers), logger.DEBUG)

                except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                    logger.log('Failed parsing provider.', logger.ERROR)

        return {'has_next_page': has_next_page, 'items': items}