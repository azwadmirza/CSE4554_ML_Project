    def get(self, name):
        ds = get_datasource(name)
        if ds is None:
            print('No valid datasource given')
            abort(400, 'No valid datasource given')

        where = []
        for key, value in request.args.items():
            if key.startswith('filter'):
                param = parse_filter(key, value)
                if param is None:
                    abort(400, f'Not valid filter "{key}"')
                where.append(param)

        data_dict = g.default_store.get_data(ds['name'], where)

        if data_dict['rowcount'] == 0:
            return abort(400, 'Empty dataset after filters applying')

        return get_analysis(pd.DataFrame(data_dict['data'])), 200