    def search(self, search_strings, age=0, ep_obj=None, **kwargs):
        """
        Search a provider and parse the results.

        :param search_strings: A dict with mode (key) and the search value (value)
        :param age: Not used
        :param ep_obj: Informations about the episode being searched (when not RSS)

        :returns: A list of search results (structure)
        """
        results = []
        if not self.login():
            return results

        manual_search = kwargs.get('manual_search')
        if manual_search:
            self.max_back_pages = 20

        anime = False
        if ep_obj and ep_obj.series:
            anime = ep_obj.series.anime == 1

        search_params = {
            'order_by': 'time',
            'order_way': 'desc',
            'group_results': 0,
            'action': 'basic',
            'searchsubmit': 1
        }

        if 'RSS' in search_strings.keys():
            search_params['filter_cat[14]'] = 1  # anime
            search_params['filter_cat[2]'] = 1  # tv shows
        elif anime:
            search_params['filter_cat[14]'] = 1  # anime
        else:
            search_params['filter_cat[2]'] = 1  # tv shows

        for mode in search_strings:
            items = []
            log.debug('Search mode: {0}'.format(mode))

            # if looking for season, look for more pages
            if mode == 'Season' and not manual_search:
                self.max_back_pages = 10

            for search_string in search_strings[mode]:
                if mode != 'RSS':
                    log.debug('Search string: {search}',
                              {'search': search_string})

                # Remove season / episode from search (not supported by tracker)
                search_str = re.sub(r'\d+$' if anime else r'[S|E]\d\d', '', search_string).strip()
                search_params['searchstr'] = search_str
                next_page = 1
                has_next_page = True

                while has_next_page and next_page <= self.max_back_pages:
                    search_params['page'] = next_page
                    log.debug('Searching page: {0}'.format(next_page))
                    next_page += 1

                    response = self.session.get(self.urls['search'], params=search_params)
                    if not response or not response.content:
                        log.debug('No data returned from provider')
                        continue

                    result = self.parse(response.content, mode)
                    has_next_page = result['has_next_page']
                    items += result['items']

                results += items

        return results