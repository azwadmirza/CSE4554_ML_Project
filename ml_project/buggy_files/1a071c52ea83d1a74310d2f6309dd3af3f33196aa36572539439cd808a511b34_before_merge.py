    def discard(self, entry):
        if self.config['list'] in IMMUTABLE_LISTS:
            raise plugin.PluginError('%s lists are not modifiable' % ' and '.join(IMMUTABLE_LISTS))
        if 'imdb_id' not in entry:
            log.warning('Cannot remove %s from imdb_list because it does not have an imdb_id', entry['title'])
            return
        # Get the list item id
        item_ids = None
        if self.config['list'] == 'watchlist':
            data = {'consts[]': entry['imdb_id'], 'tracking_tag': 'watchlistRibbon'}
            status = self.session.post('http://www.imdb.com/list/_ajax/watchlist_has', data=data).json()
            item_ids = status.get('has', {}).get(entry['imdb_id'])
        else:
            data = {'tconst': entry['imdb_id']}
            status = self.session.post('http://www.imdb.com/list/_ajax/wlb_dropdown', data=data).json()
            for a_list in status['items']:
                if a_list['data_list_id'] == self.list_id:
                    item_ids = a_list['data_list_item_ids']
                    break
        if not item_ids:
            log.warning('%s is not in list %s, cannot be removed', entry['imdb_id'], self.list_id)
            return
        data = {
            'action': 'delete',
            'list_id': self.list_id,
            'ref_tag': 'title'
        }
        for item_id in item_ids:
            self.session.post('http://www.imdb.com/list/_ajax/edit', data=dict(data, list_item_id=item_id))
        # We don't need to invalidate our cache if we remove the item
        self._items = [i for i in self._items if i['imdb_id'] != entry['imdb_id']]