    def get_data(self, df):
        form_data = self.form_data

        data = {}
        records = df.to_dict('records')
        for metric in self.metric_labels:
            values = {}
            for obj in records:
                v = obj[DTTM_ALIAS]
                if hasattr(v, 'value'):
                    v = v.value
                values[str(v / 10**9)] = obj.get(metric)
            data[metric] = values

        start, end = utils.get_since_until(form_data.get('time_range'),
                                           form_data.get('since'),
                                           form_data.get('until'))
        if not start or not end:
            raise Exception('Please provide both time bounds (Since and Until)')
        domain = form_data.get('domain_granularity')
        diff_delta = rdelta.relativedelta(end, start)
        diff_secs = (end - start).total_seconds()

        if domain == 'year':
            range_ = diff_delta.years + 1
        elif domain == 'month':
            range_ = diff_delta.years * 12 + diff_delta.months + 1
        elif domain == 'week':
            range_ = diff_delta.years * 53 + diff_delta.weeks + 1
        elif domain == 'day':
            range_ = diff_secs // (24 * 60 * 60) + 1
        else:
            range_ = diff_secs // (60 * 60) + 1

        return {
            'data': data,
            'start': start,
            'domain': domain,
            'subdomain': form_data.get('subdomain_granularity'),
            'range': range_,
        }