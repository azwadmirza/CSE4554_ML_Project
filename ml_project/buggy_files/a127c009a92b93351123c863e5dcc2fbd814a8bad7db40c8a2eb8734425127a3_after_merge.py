    def fillna(self, value=None, method=None, limit=None):
        """ Fill NA/NaN values using the specified method.

        Parameters
        ----------
        method : {'backfill', 'bfill', 'pad', 'ffill', None}, default None
            Method to use for filling holes in reindexed Series
            pad / ffill: propagate last valid observation forward to next valid
            backfill / bfill: use NEXT valid observation to fill gap
        value : scalar
            Value to use to fill holes (e.g. 0)
        limit : int, default None
            (Not implemented yet for Categorical!)
            If method is specified, this is the maximum number of consecutive
            NaN values to forward/backward fill. In other words, if there is
            a gap with more than this number of consecutive NaNs, it will only
            be partially filled. If method is not specified, this is the
            maximum number of entries along the entire axis where NaNs will be
            filled.

        Returns
        -------
        filled : Categorical with NA/NaN filled
        """

        if value is None:
            value = np.nan
        if limit is not None:
            raise NotImplementedError("specifying a limit for fillna has not "
                                      "been implemented yet")

        values = self._codes

        # Make sure that we also get NA in categories
        if self.categories.dtype.kind in ['S', 'O', 'f']:
            if np.nan in self.categories:
                values = values.copy()
                nan_pos = np.where(isnull(self.categories))[0]
                # we only have one NA in categories
                values[values == nan_pos] = -1

        # pad / bfill
        if method is not None:

            values = self.to_dense().reshape(-1, len(self))
            values = interpolate_2d(values, method, 0, None,
                                    value).astype(self.categories.dtype)[0]
            values = _get_codes_for_values(values, self.categories)

        else:

            if not isnull(value) and value not in self.categories:
                raise ValueError("fill value must be in categories")

            mask = values == -1
            if mask.any():
                values = values.copy()
                if isnull(value):
                    values[mask] = -1
                else:
                    values[mask] = self.categories.get_loc(value)

        return self._constructor(values, categories=self.categories,
                                 ordered=self.ordered, fastpath=True)