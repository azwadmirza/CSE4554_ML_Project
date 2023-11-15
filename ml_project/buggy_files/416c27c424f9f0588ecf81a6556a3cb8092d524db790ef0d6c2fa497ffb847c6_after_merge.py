    def search(self, search_strings, age=0, ep_obj=None):  # pylint: disable=too-many-locals
        results = []
        if not self.login():
            return results

        for mode in search_strings:
            items = []
            logger.log('Search mode: {0}'.format(mode), logger.DEBUG)

            for search_string in search_strings[mode]:

                if mode != 'RSS':
                    logger.log('Search string: {search}'.format
                               (search=search_string), logger.DEBUG)

                search_string = '+'.join(search_string.split())

                post_data = dict({'/browse.php?': None, 'cata': 'yes', 'jxt': 8, 'jxw': 'b', 'search': search_string},
                                 **self.categories[mode])

                if self.freeleech:
                    post_data.update({'free': 'on'})

                try:
                    response = self.get_url(self.urls['search'], post_data=post_data, returns='response')
                    response.raise_for_status()
                except RequestException as msg:
                    logger.log(u'Error while connecting to provider: {error}'.format(error=msg), logger.ERROR)
                    continue

                try:
                    jdata = response.json()
                except ValueError:  # also catches JSONDecodeError if simplejson is installed
                    logger.log('Data returned from provider is not json', logger.ERROR)
                    self.session.cookies.clear()
                    continue

                try:
                    cn = jdata.get('Fs', [dict()])[0].get('Cn', {})
                    torrents = cn.get('torrents', []) if cn else []
                except (AttributeError, TypeError, KeyError, ValueError, IndexError) as e:
                    # If TorrentDay changes their website issue will be opened so we can fix fast
                    # and not wait user notice it's not downloading torrents from there
                    logger.log('TorrentDay response: {0}. Error: {1!r}'.format(jdata, e), logger.ERROR)
                    continue

                if not torrents:
                    logger.log('Data returned from provider does not contain any torrents', logger.DEBUG)
                    continue

                for torrent in torrents:
                    try:
                        title = re.sub(r'\[.*=.*\].*\[/.*\]', '', torrent['name']) if torrent['name'] else None
                        download_url = urljoin(self.urls['download'], '{}/{}'.format(torrent['id'], torrent['fname'])) if torrent['id'] and torrent['fname'] else None
                        if not all([title, download_url]):
                            continue

                        seeders = int(torrent['seed']) if torrent['seed'] else 1
                        leechers = int(torrent['leech']) if torrent['leech'] else 0

                        # Filter unseeded torrent
                        if seeders < min(self.minseed, 1):
                            if mode != 'RSS':
                                logger.log("Discarding torrent because it doesn't meet the "
                                           "minimum seeders: {0}. Seeders: {1}".format
                                           (title, seeders), logger.DEBUG)
                            continue

                        torrent_size = torrent['size']
                        size = convert_size(torrent_size) or -1

                        item = {
                            'title': title,
                            'link': download_url,
                            'size': size,
                            'seeders': seeders,
                            'leechers': leechers,
                            'pubdate': None,
                            'hash': None,
                        }
                        if mode != 'RSS':
                            logger.log('Found result: {0} with {1} seeders and {2} leechers'.format
                                       (title, seeders, leechers), logger.DEBUG)

                        items.append(item)
                    except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                        logger.log('Failed parsing provider. Traceback: {0!r}'.format
                                   (traceback.format_exc()), logger.ERROR)
                        continue

            results += items

        return results