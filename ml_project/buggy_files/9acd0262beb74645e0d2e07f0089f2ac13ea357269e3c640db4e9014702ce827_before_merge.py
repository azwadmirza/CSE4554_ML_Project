    def sort_index(self, axis=0, level=None, ascending=True, inplace=False,
                   kind='quicksort', na_position='last', sort_remaining=True):

        inplace = validate_bool_kwarg(inplace, 'inplace')
        axis = self._get_axis_number(axis)
        index = self.index
        if level is not None:
            new_index, indexer = index.sortlevel(level, ascending=ascending,
                                                 sort_remaining=sort_remaining)
        elif isinstance(index, MultiIndex):
            from pandas.core.sorting import lexsort_indexer
            indexer = lexsort_indexer(index.labels, orders=ascending)
        else:
            from pandas.core.sorting import nargsort
            indexer = nargsort(index, kind=kind, ascending=ascending,
                               na_position=na_position)

        indexer = _ensure_platform_int(indexer)
        new_index = index.take(indexer)

        new_values = self._values.take(indexer)
        result = self._constructor(new_values, index=new_index)

        if inplace:
            self._update_inplace(result)
        else:
            return result.__finalize__(self)