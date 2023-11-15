    def _convert_to_indexer(self, obj, axis=0):
        """
        Convert indexing key into something we can use to do actual fancy
        indexing on an ndarray

        Examples
        ix[:5] -> slice(0, 5)
        ix[[1,2,3]] -> [1,2,3]
        ix[['foo', 'bar', 'baz']] -> [i, j, k] (indices of foo, bar, baz)

        Going by Zen of Python?
        "In the face of ambiguity, refuse the temptation to guess."
        raise AmbiguousIndexError with integer labels?
        - No, prefer label-based indexing
        """
        index = self.obj._get_axis(axis)
        is_int_index = _is_integer_index(index)
        if isinstance(obj, slice):
            if _is_label_slice(index, obj):
                i, j = index.slice_locs(obj.start, obj.stop)

                if obj.step is not None:
                    raise Exception('Non-zero step not supported with '
                                    'label-based slicing')
                return slice(i, j)
            else:
                return obj
        elif _is_list_like(obj):
            objarr = _asarray_tuplesafe(obj)

            if objarr.dtype == np.bool_:
                if not obj.index.equals(index):
                    raise IndexingError('Cannot use boolean index with '
                                        'misaligned or unequal labels')
                return objarr
            else:
                # If have integer labels, defer to label-based indexing
                if _is_integer_dtype(objarr) and not is_int_index:
                    return objarr

                indexer = index.get_indexer(objarr)
                mask = indexer == -1
                if mask.any():
                    raise KeyError('%s not in index' % objarr[mask])

                return indexer
        else:
            if _is_int_like(obj) and not is_int_index:
                return obj
            return index.get_loc(obj)