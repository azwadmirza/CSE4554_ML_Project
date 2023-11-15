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
        return self._engine.get_loc(codes)