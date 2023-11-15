    def _aggregate_series_fast(self, obj, func):
        func = self._is_builtin_func(func)

        if obj.index._has_complex_internals:
            raise TypeError('Incompatible index for Cython grouper')

        group_index, _, ngroups = self.group_info

        # avoids object / Series creation overhead
        dummy = obj._get_values(slice(None, 0)).to_dense()
        indexer = get_group_index_sorter(group_index, ngroups)
        obj = obj.take(indexer, convert=False)
        group_index = algorithms.take_nd(
            group_index, indexer, allow_fill=False)
        grouper = lib.SeriesGrouper(obj, func, group_index, ngroups,
                                    dummy)
        result, counts = grouper.get_result()
        return result, counts