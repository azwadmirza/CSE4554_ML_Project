    def search(self, search_strings, age=0, ep_obj=None):
        """
        Searche indexer using the params in search_strings, either for latest releases, or a string/id search.

        Returns: list of results in dict form
        """
        results = []
        if not self._check_auth():
            return results

        # For providers that don't have caps, or for which the t=caps is not working.
        if not self.caps and all(provider not in self.url for provider in self.providers_without_caps):
            self.get_newznab_categories(just_caps=True)
            if not self.caps:
                return results

        for mode in search_strings:
            self.torznab = False
            search_params = {
                't': 'search',
                'limit': 100,
                'offset': 0,
                'cat': self.cat_ids.strip(', ') or '5030,5040',
                'maxage': app.USENET_RETENTION
            }

            if self.needs_auth and self.key:
                search_params['apikey'] = self.key

            if mode != 'RSS':
                match_indexer = self._match_indexer()
                search_params['t'] = 'tvsearch' if match_indexer and not self.force_query else 'search'

                if search_params['t'] == 'tvsearch':
                    search_params.update(match_indexer)

                    if ep_obj.show.air_by_date or ep_obj.show.sports:
                        date_str = str(ep_obj.airdate)
                        search_params['season'] = date_str.partition('-')[0]
                        search_params['ep'] = date_str.partition('-')[2].replace('-', '/')
                    else:
                        search_params['season'] = ep_obj.scene_season
                        search_params['ep'] = ep_obj.scene_episode

                if mode == 'Season':
                    search_params.pop('ep', '')

            items = []
            logger.log('Search mode: {0}'.format(mode), logger.DEBUG)

            for search_string in search_strings[mode]:

                if mode != 'RSS':
                    # If its a PROPER search, need to change param to 'search' so it searches using 'q' param
                    if any(proper_string in search_string for proper_string in self.proper_strings):
                        search_params['t'] = 'search'

                    logger.log('Search show using {search}'.format
                               (search='search string: {search_string}'.format(search_string=search_string if
                                search_params['t'] != 'tvsearch' else
                                'indexer_id: {indexer_id}'.format(indexer_id=match_indexer))),
                               logger.DEBUG)

                    if search_params['t'] != 'tvsearch':
                        search_params['q'] = search_string

                time.sleep(cpu_presets[app.CPU_PRESET])

                response = self.get_url(urljoin(self.url, 'api'), params=search_params, returns='response')
                if not response or not response.text:
                    logger.log('No data returned from provider', logger.DEBUG)
                    continue

                with BS4Parser(response.text, 'html5lib') as html:
                    if not self._check_auth_from_data(html):
                        return items

                    try:
                        self.torznab = 'xmlns:torznab' in html.rss.attrs
                    except AttributeError:
                        self.torznab = False

                    for item in html('item'):
                        try:
                            title = item.title.get_text(strip=True)
                            download_url = None
                            if item.link:
                                if validators.url(item.link.get_text(strip=True)):
                                    download_url = item.link.get_text(strip=True)
                                elif validators.url(item.link.next.strip()):
                                    download_url = item.link.next.strip()

                            if not download_url and item.enclosure:
                                if validators.url(item.enclosure.get('url', '').strip()):
                                    download_url = item.enclosure.get('url', '').strip()

                            if not (title and download_url):
                                continue

                            seeders = leechers = -1
                            if 'gingadaddy' in self.url:
                                size_regex = re.search(r'\d*.?\d* [KMGT]B', str(item.description))
                                item_size = size_regex.group() if size_regex else -1
                            else:
                                item_size = item.size.get_text(strip=True) if item.size else -1
                                for attr in item('newznab:attr') + item('torznab:attr'):
                                    item_size = attr['value'] if attr['name'] == 'size' else item_size
                                    seeders = try_int(attr['value']) if attr['name'] == 'seeders' else seeders
                                    peers = try_int(attr['value']) if attr['name'] == 'peers' else None
                                    leechers = peers - seeders if peers else leechers

                            if not item_size or (self.torznab and (seeders is -1 or leechers is -1)):
                                continue

                            size = convert_size(item_size) or -1
                            pubdate_raw = item.pubdate.get_text(strip=True)
                            try:
                                pubdate = parser.parse(pubdate_raw, fuzzy=True) if pubdate_raw else None
                            except ValueError:
                                pubdate = None

                            item = {
                                'title': title,
                                'link': download_url,
                                'size': size,
                                'seeders': seeders,
                                'leechers': leechers,
                                'pubdate': pubdate,
                                'torrent_hash': None,
                            }
                            if mode != 'RSS':
                                if seeders == -1:
                                    logger.log('Found result: {0}'.format(title), logger.DEBUG)
                                else:
                                    logger.log('Found result: {0} with {1} seeders and {2} leechers'.format
                                               (title, seeders, leechers), logger.DEBUG)

                            items.append(item)
                        except (AttributeError, TypeError, KeyError, ValueError, IndexError):
                            logger.log('Failed parsing provider. Traceback: {0!r}'.format
                                       (traceback.format_exc()), logger.ERROR)
                            continue

                # Since we arent using the search string,
                # break out of the search string loop
                if 'tvdbid' in search_params:
                    break

            results += items

        # Reproces but now use force_query = True
        if not results and not self.force_query:
            self.force_query = True
            return self.search(search_strings, ep_obj=ep_obj)

        return results