    def _get_listlike_indexer(self, key, axis: int, raise_missing: bool = False):
        """
        Transform a list-like of keys into a new index and an indexer.

        Parameters
        ----------
        key : list-like
            Targeted labels.
        axis: int
            Dimension on which the indexing is being made.
        raise_missing: bool, default False
            Whether to raise a KeyError if some labels were not found.
            Will be removed in the future, and then this method will always behave as
            if ``raise_missing=True``.

        Raises
        ------
        KeyError
            If at least one key was requested but none was found, and
            raise_missing=True.

        Returns
        -------
        keyarr: Index
            New index (coinciding with 'key' if the axis is unique).
        values : array-like
            Indexer for the return object, -1 denotes keys not found.
        """
        ax = self.obj._get_axis(axis)

        # Have the index compute an indexer or return None
        # if it cannot handle:
        indexer, keyarr = ax._convert_listlike_indexer(key)
        # We only act on all found values:
        if indexer is not None and (indexer != -1).all():
            self._validate_read_indexer(key, indexer, axis, raise_missing=raise_missing)
            return ax[indexer], indexer

        if ax.is_unique and not getattr(ax, "is_overlapping", False):
            indexer = ax.get_indexer_for(key)
            keyarr = ax.reindex(keyarr)[0]
        else:
            keyarr, indexer, new_indexer = ax._reindex_non_unique(keyarr)

        self._validate_read_indexer(keyarr, indexer, axis, raise_missing=raise_missing)
        return keyarr, indexer