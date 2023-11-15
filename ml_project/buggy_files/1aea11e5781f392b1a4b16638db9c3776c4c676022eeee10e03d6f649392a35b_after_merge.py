    def on_task_input(self, task, config):
        email = config.get('email')
        log.info('Retrieving npo.nl watchlist for %s', email)

        response = self._get_page(task, config, 'https://www.npo.nl/mijn_npo')
        page = get_soup(response.content)

        entries = self._get_watchlist_entries(task, config, page)
        entries += self._get_favorites_entries(task, config, page)

        return entries