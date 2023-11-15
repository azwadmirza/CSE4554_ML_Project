    def process_data(self):
        """Take the CategoricalHeatMap data from the input **value.

        It calculates the chart properties accordingly. Then build a dict
        containing references to all the calculated points to be used by
        the rect glyph inside the ``_yield_renderers`` method.

        """
        for op in self._data.operations:
            if isinstance(op, Bins):
                self.bin_width = op.get_dim_width('x')
                self.bin_height = op.get_dim_width('y')
                self._bins = op

        # if we have values specified but color attribute not setup, do so
        if self.attributes['color'].columns is None:
            self.attributes['color'].setup(data=self._data.source,
                                           columns=self.values.selection or 'values')
        self.attributes['color'].add_bin_labels(self._data)