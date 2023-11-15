    def search(self, search_strings, age=0, ep_obj=None, **kwargs):
        """
        Search a provider and parse the results.

        :param search_strings: A dict with mode (key) and the search value (value)
        :param age: Not used
        :param ep_obj: Not used
        :returns: A list of search results (structure)
        """
        results = []
        if not self.login():
            return results

        for mode in search_strings:
            log.debug('Search mode: {0}', mode)

            for search_string in search_strings[mode]:
                if mode != 'RSS':
                    log.debug('Search string: {search}',
                              {'search': search_string})

                search_string = '+'.join(search_string.split())

                params = dict({'q': search_string}, **self.categories[mode])

                response = self.session.get(self.urls['search'], params=params)
                if not response or not response.text:
                    log.debug('No data returned from provider')
                    continue

                try:
                    jdata = djson.loads(response.text)
                except ValueError as error:
                    log.error("Couldn't deserialize JSON document. Error: {0!r}", error)
                    continue

                results += self.parse(jdata, mode)

        return results