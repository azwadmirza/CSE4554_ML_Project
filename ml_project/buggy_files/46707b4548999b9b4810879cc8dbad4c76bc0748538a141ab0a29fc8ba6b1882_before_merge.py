    def query_obj(self):
        form_data = self.form_data
        d = super().query_obj()
        d['groupby'] = [
            form_data.get('entity'),
        ]
        if form_data.get('series'):
            d['groupby'].append(form_data.get('series'))
        self.x_metric = form_data.get('x')
        self.y_metric = form_data.get('y')
        self.z_metric = form_data.get('size')
        self.entity = form_data.get('entity')
        self.series = form_data.get('series') or self.entity
        d['row_limit'] = form_data.get('limit')

        d['metrics'] = [
            self.z_metric,
            self.x_metric,
            self.y_metric,
        ]
        if not all(d['metrics'] + [self.entity]):
            raise Exception(_('Pick a metric for x, y and size'))
        return d