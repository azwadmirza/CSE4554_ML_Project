    def _multi_take(self, tup):
        """ create the reindex map for our objects, raise the _exception if we
        can't create the indexer
        """
        try:
            o = self.obj
            d = {a: self._convert_for_reindex(t, axis=o._get_axis_number(a))
                 for t, a in zip(tup, o._AXIS_ORDERS)}
            return o.reindex(**d)
        except(KeyError, IndexingError):
            raise self._exception