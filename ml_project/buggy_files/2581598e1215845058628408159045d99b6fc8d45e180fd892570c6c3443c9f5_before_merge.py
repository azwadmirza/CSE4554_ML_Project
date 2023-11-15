    def _concat_objects(self, keys, values, not_indexed_same: bool = False):
        from pandas.core.reshape.concat import concat

        def reset_identity(values):
            # reset the identities of the components
            # of the values to prevent aliasing
            for v in com.not_none(*values):
                ax = v._get_axis(self.axis)
                ax._reset_identity()
            return values

        if not not_indexed_same:
            result = concat(values, axis=self.axis)
            ax = self._selected_obj._get_axis(self.axis)

            if isinstance(result, Series):
                result = result.reindex(ax)
            else:

                # this is a very unfortunate situation
                # we have a multi-index that is NOT lexsorted
                # and we have a result which is duplicated
                # we can't reindex, so we resort to this
                # GH 14776
                if isinstance(ax, MultiIndex) and not ax.is_unique:
                    indexer = algorithms.unique1d(
                        result.index.get_indexer_for(ax.values)
                    )
                    result = result.take(indexer, axis=self.axis)
                else:
                    result = result.reindex(ax, axis=self.axis)

        elif self.group_keys:

            values = reset_identity(values)
            if self.as_index:

                # possible MI return case
                group_keys = keys
                group_levels = self.grouper.levels
                group_names = self.grouper.names

                result = concat(
                    values,
                    axis=self.axis,
                    keys=group_keys,
                    levels=group_levels,
                    names=group_names,
                    sort=False,
                )
            else:

                # GH5610, returns a MI, with the first level being a
                # range index
                keys = list(range(len(values)))
                result = concat(values, axis=self.axis, keys=keys)
        else:
            values = reset_identity(values)
            result = concat(values, axis=self.axis)

        if isinstance(result, Series) and self._selection_name is not None:

            result.name = self._selection_name

        return result