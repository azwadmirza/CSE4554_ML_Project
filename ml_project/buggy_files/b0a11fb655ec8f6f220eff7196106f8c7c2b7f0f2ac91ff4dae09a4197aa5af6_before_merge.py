    def get_loc(self, key, method=None):
        """
        Get integer location for requested label

        Parameters
        ----------
        key : label
        method : {None}
            * default: exact matches only.

        Returns
        -------
        loc : int if unique index, possibly slice or mask if not
        """
        codes = self.categories.get_loc(key)
        if (codes == -1):
            raise KeyError(key)
        indexer, _ = self._engine.get_indexer_non_unique(np.array([codes]))
        if (indexer == -1).any():
            raise KeyError(key)

        return indexer