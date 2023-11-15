    def _upsample(self, method, limit=None):
        """
        method : string {'backfill', 'bfill', 'pad', 'ffill'}
            method for upsampling
        limit : int, default None
            Maximum size gap to fill when reindexing

        See also
        --------
        .fillna

        """
        # we may need to actually resample as if we are timestamps
        if self.kind == 'timestamp':
            return super(PeriodIndexResampler, self)._upsample(method,
                                                               limit=limit)

        ax = self.ax
        obj = self.obj
        new_index = self._get_new_index()

        if len(new_index) == 0:
            return self._wrap_result(self._selected_obj.reindex(new_index))

        # Start vs. end of period
        memb = ax.asfreq(self.freq, how=self.convention)

        # Get the fill indexer
        indexer = memb.get_indexer(new_index, method=method, limit=limit)
        return self._wrap_result(_take_new_index(
            obj, indexer, new_index, axis=self.axis))