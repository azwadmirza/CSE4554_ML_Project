    def _wrap_applied_output(
        self, keys: Index, values: Optional[List[Any]], not_indexed_same: bool = False
    ) -> FrameOrSeriesUnion:
        """
        Wrap the output of SeriesGroupBy.apply into the expected result.

        Parameters
        ----------
        keys : Index
            Keys of groups that Series was grouped by.
        values : Optional[List[Any]]
            Applied output for each group.
        not_indexed_same : bool, default False
            Whether the applied outputs are not indexed the same as the group axes.

        Returns
        -------
        DataFrame or Series
        """
        if len(keys) == 0:
            # GH #6265
            return self.obj._constructor(
                [], name=self._selection_name, index=keys, dtype=np.float64
            )
        assert values is not None

        def _get_index() -> Index:
            if self.grouper.nkeys > 1:
                index = MultiIndex.from_tuples(keys, names=self.grouper.names)
            else:
                index = Index(keys, name=self.grouper.names[0])
            return index

        if isinstance(values[0], dict):
            # GH #823 #24880
            index = _get_index()
            result: FrameOrSeriesUnion = self._reindex_output(
                self.obj._constructor_expanddim(values, index=index)
            )
            # if self.observed is False,
            # keep all-NaN rows created while re-indexing
            result = result.stack(dropna=self.observed)
            result.name = self._selection_name
            return result
        elif isinstance(values[0], (Series, DataFrame)):
            return self._concat_objects(keys, values, not_indexed_same=not_indexed_same)
        else:
            # GH #6265 #24880
            result = self.obj._constructor(
                data=values, index=_get_index(), name=self._selection_name
            )
            return self._reindex_output(result)