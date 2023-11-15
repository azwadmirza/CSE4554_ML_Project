    def _getitem_iterable(self, key, axis=None):
        if axis is None:
            axis = self.axis or 0

        if self._should_validate_iterable(axis):
            self._has_valid_type(key, axis)

        labels = self.obj._get_axis(axis)

        if com.is_bool_indexer(key):
            key = check_bool_indexer(labels, key)
            inds, = key.nonzero()
            return self.obj._take(inds, axis=axis, convert=False)
        else:
            # Have the index compute an indexer or return None
            # if it cannot handle; we only act on all found values
            indexer, keyarr = labels._convert_listlike_indexer(
                key, kind=self.name)
            if indexer is not None and (indexer != -1).all():
                return self.obj.take(indexer, axis=axis)

            # existing labels are unique and indexer are unique
            if labels.is_unique and Index(keyarr).is_unique:

                try:
                    return self.obj.reindex(keyarr, axis=axis)
                except AttributeError:

                    # Series
                    if axis != 0:
                        raise AssertionError('axis must be 0')
                    return self.obj.reindex(keyarr)

            # existing labels are non-unique
            else:

                # reindex with the specified axis
                if axis + 1 > self.obj.ndim:
                    raise AssertionError("invalid indexing error with "
                                         "non-unique index")

                new_target, indexer, new_indexer = labels._reindex_non_unique(
                    keyarr)

                if new_indexer is not None:
                    result = self.obj._take(indexer[indexer != -1], axis=axis,
                                            convert=False)

                    result = result._reindex_with_indexers(
                        {axis: [new_target, new_indexer]},
                        copy=True, allow_dups=True)

                else:
                    result = self.obj._take(indexer, axis=axis)

                return result