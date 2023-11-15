    def asof(self, where, subset=None):
        """
        The last row without any NaN is taken (or the last row without
        NaN considering only the subset of columns in the case of a DataFrame)

        .. versionadded:: 0.19.0 For DataFrame

        If there is no good value, NaN is returned for a Series
        a Series of NaN values for a DataFrame

        Parameters
        ----------
        where : date or array of dates
        subset : string or list of strings, default None
           if not None use these columns for NaN propagation

        Notes
        -----
        Dates are assumed to be sorted
        Raises if this is not the case

        Returns
        -------
        where is scalar

          - value or NaN if input is Series
          - Series if input is DataFrame

        where is Index: same shape object as input

        See Also
        --------
        merge_asof

        """

        if isinstance(where, compat.string_types):
            from pandas import to_datetime
            where = to_datetime(where)

        if not self.index.is_monotonic:
            raise ValueError("asof requires a sorted index")

        is_series = isinstance(self, ABCSeries)
        if is_series:
            if subset is not None:
                raise ValueError("subset is not valid for Series")
        elif self.ndim > 2:
            raise NotImplementedError("asof is not implemented "
                                      "for {type}".format(type(self)))
        else:
            if subset is None:
                subset = self.columns
            if not is_list_like(subset):
                subset = [subset]

        is_list = is_list_like(where)
        if not is_list:
            start = self.index[0]
            if isinstance(self.index, PeriodIndex):
                where = Period(where, freq=self.index.freq).ordinal
                start = start.ordinal

            if where < start:
                if not is_series:
                    from pandas import Series
                    return Series(index=self.columns, name=where)
                return np.nan

            # It's always much faster to use a *while* loop here for
            # Series than pre-computing all the NAs. However a
            # *while* loop is extremely expensive for DataFrame
            # so we later pre-compute all the NAs and use the same
            # code path whether *where* is a scalar or list.
            # See PR: https://github.com/pandas-dev/pandas/pull/14476
            if is_series:
                loc = self.index.searchsorted(where, side='right')
                if loc > 0:
                    loc -= 1

                values = self._values
                while loc > 0 and isnull(values[loc]):
                    loc -= 1
                return values[loc]

        if not isinstance(where, Index):
            where = Index(where) if is_list else Index([where])

        nulls = self.isnull() if is_series else self[subset].isnull().any(1)
        locs = self.index.asof_locs(where, ~(nulls.values))

        # mask the missing
        missing = locs == -1
        data = self.take(locs, is_copy=False)
        data.index = where
        data.loc[missing] = np.nan
        return data if is_list else data.iloc[-1]