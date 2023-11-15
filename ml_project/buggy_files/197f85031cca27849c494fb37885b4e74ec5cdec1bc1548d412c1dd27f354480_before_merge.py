    def shift(self, periods, offset=None, timeRule=None):
        """
        Analogous to DataFrame.shift
        """
        if timeRule is not None and offset is None:
            offset = datetools.getOffset(timeRule)

        new_series = {}
        if offset is None:
            new_index = self.index
            for col, s in self.iteritems():
                new_series[col] = s.shift(periods)
        else:
            new_index = self.index.shift(periods, offset)
            for col, s in self.iteritems():
                new_series[col] = SparseSeries(s.sp_values, index=new_index,
                                               sparse_index=s.sp_index,
                                               fill_value=s.fill_value)

        return SparseDataFrame(new_series, index=new_index,
                               columns=self.columns,
                               default_fill_value=self.default_fill_value,
                               default_kind=self.default_kind)