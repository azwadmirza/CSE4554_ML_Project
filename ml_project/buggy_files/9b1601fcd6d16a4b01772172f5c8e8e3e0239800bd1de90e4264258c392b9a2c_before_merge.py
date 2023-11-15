    def get(self, name):
        '''return data rows'''
        ds = g.default_store.get_datasource(name)
        if ds is None:
            abort(400, 'No valid datasource given')

        params = {
            'page[size]': None,
            'page[offset]': None
        }
        where = []
        for key, value in request.args.items():
            if key == 'page[size]':
                params['page[size]'] = int(value)
            if key == 'page[offset]':
                params['page[offset]'] = int(value)
            elif key.startswith('filter'):
                param = parse_filter(key, value)
                if param is None:
                    abort(400, f'Not valid filter "{key}"')
                where.append(param)

        data_dict = g.default_store.get_data(name, where, params['page[size]'], params['page[offset]'])

        return data_dict, 200