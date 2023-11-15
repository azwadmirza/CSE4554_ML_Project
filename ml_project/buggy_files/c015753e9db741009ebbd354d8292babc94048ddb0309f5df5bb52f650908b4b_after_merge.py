    def _update_datasource(self, source, data):
        """
        Update datasource with data for a new frame.
        """
        if isinstance(source, ColumnDataSource):
            if self.handles['static_source']:
                source.trigger('data', source.data, data)
            else:
                source.data.update(data)
        else:
            source.graph_layout = data