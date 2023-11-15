    def count(self, level=None):
        """
        Return number of non-NA/null observations in the Series

        Parameters
        ----------
        level : int or level name, default None
            If the axis is a MultiIndex (hierarchical), count along a
            particular level, collapsing into a smaller Series

        Returns
        -------
        nobs : int or Series (if level specified)
        """
        from pandas.core.index import _get_na_value

        if level is None:
            return notnull(_values_from_object(self)).sum()

        if isinstance(level, compat.string_types):
            level = self.index._get_level_number(level)

        lev = self.index.levels[level]
        lab = np.array(self.index.labels[level], subok=False, copy=True)

        mask = lab == -1
        if mask.any():
            lab[mask] = cnt = len(lev)
            lev = lev.insert(cnt, _get_na_value(lev.dtype.type))

        out = np.bincount(lab[notnull(self.values)], minlength=len(lev))
        return self._constructor(out, index=lev, dtype='int64').__finalize__(self)