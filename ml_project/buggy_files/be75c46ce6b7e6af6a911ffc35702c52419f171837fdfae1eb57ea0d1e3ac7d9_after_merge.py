    def _get_watchlist_entries(self, task, config, page):
        watchlist = page.find('div', attrs={'id': 'component-grid-watchlist'})
        return self._parse_tiles(task, config, watchlist)