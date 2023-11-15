    def search(self, search_strings, **kwargs):
        """
        Search a provider and parse the results.

        :param search_strings: A dict with mode (key) and the search value (value)
        :returns: A list of search results (structure)
        """
        results = []
        search_params = {
            'adv_age': '',
            'xminsize': 20,
            'max': 250,
        }
        groups = [1, 2]

        for mode in search_strings:
            log.debug('Search mode: {0}', mode)
            # https://www.binsearch.info/browse.php?bg=alt.binaries.teevee&server=2
            for search_string in search_strings[mode]:
                search_params['q'] = search_string
                for group in groups:
                    # Try both 'search in the most popular groups' & 'search in the other groups' modes
                    search_params['server'] = group
                    if mode != 'RSS':
                        log.debug('Search string: {search}', {'search': search_string})
                        search_url = self.urls['search']
                    else:
                        search_params = {
                            'bg': 'alt.binaries.teevee',
                            'server': 2,
                            'max': 50,
                        }
                        search_url = self.urls['rss']
                    response = self.session.get(search_url, params=search_params)
                    if not response:
                        log.debug('No data returned from provider')
                        continue

                    results += self.parse(response.text, mode)

        return results