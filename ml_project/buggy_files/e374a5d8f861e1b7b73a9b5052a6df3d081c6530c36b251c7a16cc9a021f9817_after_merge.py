    def on_task_input(self, task, config):
        config = self.prepare_config(config)

        # Create movie entries by parsing imdb list page(s) html using beautifulsoup
        log.verbose('Retrieving imdb list: %s', config['list'])

        headers = {'Accept-Language': config.get('force_language')}
        params = {'view': 'detail', 'page': 1}
        if config['list'] in ['watchlist', 'ratings', 'checkins']:
            url = 'http://www.imdb.com/user/%s/%s' % (config['user_id'], config['list'])
            if config['list'] == 'watchlist':
                params = {'view': 'detail'}
        else:
            url = 'http://www.imdb.com/list/%s' % config['list']
        if 'all' not in config['type']:
            title_types = [TITLE_TYPE_MAP[title_type] for title_type in config['type']]
            params['title_type'] = ','.join(title_types)
            params['sort'] = 'list_order%2Casc'

        if config['list'] == 'watchlist':
            entries = self.parse_react_widget(task, config, url, params, headers)
        else:
            entries = self.parse_html_list(task, config, url, params, headers)
        return entries