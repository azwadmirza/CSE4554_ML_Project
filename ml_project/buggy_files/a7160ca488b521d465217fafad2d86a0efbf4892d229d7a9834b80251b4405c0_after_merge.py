    def sort_index(self, axis=0, level=None, ascending=True, inplace=False,
                   kind='quicksort', na_position='last', sort_remaining=True,
                   by=None):

        # TODO: this can be combined with Series.sort_index impl as
        # almost identical

        inplace = validate_bool_kwarg(inplace, 'inplace')
        # 10726
        if by is not None:
            warnings.warn("by argument to sort_index is deprecated, pls use "
                          ".sort_values(by=...)", FutureWarning, stacklevel=2)
            if level is not None:
                raise ValueError("unable to simultaneously sort by and level")
            return self.sort_values(by, axis=axis, ascending=ascending,
                                    inplace=inplace)

        axis = self._get_axis_number(axis)
        labels = self._get_axis(axis)

        if level:

            new_axis, indexer = labels.sortlevel(level, ascending=ascending,
                                                 sort_remaining=sort_remaining)

        elif isinstance(labels, MultiIndex):
            from pandas.core.sorting import lexsort_indexer

            # make sure that the axis is lexsorted to start
            # if not we need to reconstruct to get the correct indexer
            labels = labels._sort_levels_monotonic()
            indexer = lexsort_indexer(labels.labels, orders=ascending,
                                      na_position=na_position)
        else:
            from pandas.core.sorting import nargsort

            # Check monotonic-ness before sort an index
            # GH11080
            if ((ascending and labels.is_monotonic_increasing) or
                    (not ascending and labels.is_monotonic_decreasing)):
                if inplace:
                    return
                else:
                    return self.copy()

            indexer = nargsort(labels, kind=kind, ascending=ascending,
                               na_position=na_position)

        baxis = self._get_block_manager_axis(axis)
        new_data = self._data.take(indexer,
                                   axis=baxis,
                                   convert=False, verify=False)

        if inplace:
            return self._update_inplace(new_data)
        else:
            return self._constructor(new_data).__finalize__(self)