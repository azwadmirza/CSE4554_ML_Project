    def _multi_take(self, tup):
        """ create the reindex map for our objects, raise the _exception if we
        can't create the indexer
        """
        try:
            o = self.obj
            d = {}
            for key, axis in zip(tup, o._AXIS_ORDERS):
                ax = o._get_axis(axis)
                # Have the index compute an indexer or return None
                # if it cannot handle:
                indexer, keyarr = ax._convert_listlike_indexer(key,
                                                               kind=self.name)
                # We only act on all found values:
                if indexer is not None and (indexer != -1).all():
                    self._validate_read_indexer(key, indexer, axis)
                    d[axis] = (ax[indexer], indexer)
                    continue

                # If we are trying to get actual keys from empty Series, we
                # patiently wait for a KeyError later on - otherwise, convert
                if len(ax) or not len(key):
                    key = self._convert_for_reindex(key, axis)
                indexer = ax.get_indexer_for(key)
                keyarr = ax.reindex(keyarr)[0]
                self._validate_read_indexer(keyarr, indexer,
                                            o._get_axis_number(axis))
                d[axis] = (keyarr, indexer)
            return o._reindex_with_indexers(d, copy=True, allow_dups=True)
        except (KeyError, IndexingError) as detail:
            raise self._exception(detail)