    def search(self, search_params, age=0, ep_obj=None):  # pylint: disable=too-many-locals
        results = []
        if not self.login():
            return results

        for mode in search_params:
            items = []
            logger.log(u"Search Mode: {}".format(mode), logger.DEBUG)
            for search_string in search_params[mode]:

                if mode != 'RSS':
                    logger.log(u"Search string: {}".format(search_string.decode("utf-8")),
                               logger.DEBUG)

                search_string = '+'.join(search_string.split())

                post_data = dict({'/browse.php?': None, 'cata': 'yes', 'jxt': 8, 'jxw': 'b', 'search': search_string},
                                 **self.categories[mode])

                if self.freeleech:
                    post_data.update({'free': 'on'})

                try:
                    response = self.get_url(self.urls['search'], post_data=post_data)
                    response.raise_for_status()
                except RequestException as msg:
                    logger.log(u'Error while connecting to provider: {error}'.format(error=msg), logger.ERROR)
                    continue

                try:
                    jdata = response.json()
                except ValueError:  # also catches JSONDecodeError if simplejson is installed
                    logger.log(u"Data returned from provider is not json", logger.ERROR)
                    continue

                torrents = jdata.get('Fs', [dict()])[0].get('Cn', {}).get('torrents', [])
                if not torrents:
                    logger.log(u"Data returned from provider does not contain any torrents", logger.DEBUG)
                    continue

                for torrent in torrents:
                    title = re.sub(r"\[.*\=.*\].*\[/.*\]", "", torrent['name']) if torrent['name'] else None
                    download_url = urljoin(self.urls['download'], '{}/{}'.format(torrent['id'], torrent['fname'])) if torrent['id'] and torrent['fname'] else None

                    if not all([title, download_url]):
                        continue

                    seeders = int(torrent['seed']) if torrent['seed'] else 1
                    leechers = int(torrent['leech']) if torrent['leech'] else 0

                    # Filter unseeded torrent
                    if seeders < min(self.minseed, 1):
                        if mode != 'RSS':
                            logger.log(u"Discarding torrent because it doesn't meet the minimum seeders: {0}. Seeders: {1})".format(title, seeders), logger.DEBUG)
                        continue

                    torrent_size = torrent['size']
                    size = convert_size(torrent_size) or -1

                    item = {'title': title, 'link': download_url, 'size': size, 'seeders': seeders, 'leechers': leechers, 'pubdate': None, 'hash': None}

                    if mode != 'RSS':
                        logger.log(u"Found result: {0} with {1} seeders and {2} leechers".format
                                   (title, seeders, leechers), logger.DEBUG)

                    items.append(item)

            # For each search mode sort all the items by seeders if available
            items.sort(key=lambda d: try_int(d.get('seeders', 0)), reverse=True)
            results += items

        return results