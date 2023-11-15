    def nunique(self, axis: int = 0, dropna: bool = True, approx: bool = False,
                rsd: float = 0.05) -> pd.Series:
        """
        Return number of unique elements in the object.

        Excludes NA values by default.

        Parameters
        ----------
        axis : int, default 0
            Can only be set to 0 at the moment.
        dropna : bool, default True
            Don’t include NaN in the count.
        approx: bool, default False
            If False, will use the exact algorithm and return the exact number of unique.
            If True, it uses the HyperLogLog approximate algorithm, which is significantly faster
            for large amount of data.
            Note: This parameter is specific to Koalas and is not found in pandas.
        rsd: float, default 0.05
            Maximum estimation error allowed in the HyperLogLog algorithm.
            Note: Just like ``approx`` this parameter is specific to Koalas.

        Returns
        -------
        The number of unique values per column as a pandas Series.

        Examples
        --------
        >>> df = ks.DataFrame({'A': [1, 2, 3], 'B': [np.nan, 3, np.nan]})
        >>> df.nunique()
        A    3
        B    1
        Name: 0, dtype: int64

        >>> df.nunique(dropna=False)
        A    3
        B    2
        Name: 0, dtype: int64

        On big data, we recommend using the approximate algorithm to speed up this function.
        The result will be very close to the exact unique count.

        >>> df.nunique(approx=True)
        A    3
        B    1
        Name: 0, dtype: int64
        """
        if axis != 0:
            raise ValueError("The 'nunique' method only works with axis=0 at the moment")
        count_fn = partial(F.approx_count_distinct, rsd=rsd) if approx else F.countDistinct
        if dropna:
            res = self._sdf.select([count_fn(Column(c))
                                   .alias(c)
                                    for c in self.columns])
        else:
            res = self._sdf.select([(count_fn(Column(c))
                                     # If the count of null values in a column is at least 1,
                                     # increase the total count by 1 else 0. This is like adding
                                     # self.isnull().sum().clip(upper=1) but can be computed in a
                                     # single Spark job when pulling it into the select statement.
                                     + F.when(F.count(F.when(F.col(c).isNull(), 1).otherwise(None))
                                              >= 1, 1).otherwise(0))
                                   .alias(c)
                                    for c in self.columns])
        return res.toPandas().T.iloc[:, 0]