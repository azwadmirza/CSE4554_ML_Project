    def get_data(self, df):
        from superset.data import countries
        fd = self.form_data
        cols = [fd.get('entity')]
        metric = utils.get_metric_name(fd.get('metric'))
        secondary_metric = utils.get_metric_name(fd.get('secondary_metric'))
        columns = ['country', 'm1', 'm2']
        if metric == secondary_metric:
            ndf = df[cols]
            # df[metric] will be a DataFrame
            # because there are duplicate column names
            ndf['m1'] = df[metric].iloc[:, 0]
            ndf['m2'] = ndf['m1']
        else:
            if secondary_metric:
                cols += [metric, secondary_metric]
            else:
                cols += [metric]
                columns = ['country', 'm1']
            ndf = df[cols]
        df = ndf
        df.columns = columns
        d = df.to_dict(orient='records')
        for row in d:
            country = None
            if isinstance(row['country'], str):
                country = countries.get(
                    fd.get('country_fieldtype'), row['country'])

            if country:
                row['country'] = country['cca3']
                row['latitude'] = country['lat']
                row['longitude'] = country['lng']
                row['name'] = country['name']
            else:
                row['country'] = 'XXX'
        return d