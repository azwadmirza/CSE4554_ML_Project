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
        labels = self.obj._get_axis(axis)
        is_int_index = _is_integer_index(labels)

        if com.is_integer(obj) and not is_int_index:
            return obj

        try:
            return labels.get_loc(obj)
        except (KeyError, TypeError):
            pass

        if isinstance(obj, slice):

            int_slice = _is_index_slice(obj)
            null_slice = obj.start is None and obj.stop is None
            # could have integers in the first level of the MultiIndex
            position_slice = (int_slice
                              and not labels.inferred_type == 'integer'
                              and not isinstance(labels, MultiIndex))

            start, stop = obj.start, obj.stop

            # last ditch effort: if we are mixed and have integers
            try:
                if 'mixed' in labels.inferred_type and int_slice:
                    if start is not None:
                        i = labels.get_loc(start)
                    if stop is not None:
                        j = labels.get_loc(stop)
                    position_slice = False
            except KeyError:
                if labels.inferred_type == 'mixed-integer':
                    raise

            if null_slice or position_slice:
                slicer = obj
            else:
                try:
                    i, j = labels.slice_locs(start, stop)
                    slicer = slice(i, j, obj.step)
                except Exception:
                    if _is_index_slice(obj):
                        if labels.inferred_type == 'integer':
                            raise
                        slicer = obj
                    else:
                        raise

            return slicer

        elif _is_list_like(obj):
            if com._is_bool_indexer(obj):
                objarr = _check_bool_indexer(labels, obj)
                return objarr
            else:
                objarr = _asarray_tuplesafe(obj)

                # If have integer labels, defer to label-based indexing
                if _is_integer_dtype(objarr) and not is_int_index:
                    return objarr

                # this is not the most robust, but...
                if (isinstance(labels, MultiIndex) and
                    not isinstance(objarr[0], tuple)):
                    level = 0
                    _, indexer = labels.reindex(objarr, level=level)

                    check = labels.levels[0].get_indexer(objarr)
                else:
                    level = None
                    indexer = check = labels.get_indexer(objarr)

                mask = check == -1
                if mask.any():
                    raise KeyError('%s not in index' % objarr[mask])

                return indexer
        else:
            return labels.get_loc(obj)