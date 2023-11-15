    def merge(
        self,
        right,
        how="inner",
        on=None,
        left_on=None,
        right_on=None,
        left_index=False,
        right_index=False,
        sort=False,
        suffixes=("_x", "_y"),
        copy=True,
        indicator=False,
        validate=None,
    ):
        """
        Merge DataFrame or named Series objects with a database-style join.

        The join is done on columns or indexes. If joining columns on columns,
        the DataFrame indexes will be ignored. Otherwise if joining indexes on indexes or
        indexes on a column or columns, the index will be passed on.

        Parameters
        ----------
        right : DataFrame or named Series
            Object to merge with.
        how : {'left', 'right', 'outer', 'inner'}, default 'inner'
            Type of merge to be performed.
            - left: use only keys from left frame,
              similar to a SQL left outer join; preserve key order.
            - right: use only keys from right frame,
              similar to a SQL right outer join; preserve key order.
            - outer: use union of keys from both frames,
              similar to a SQL full outer join; sort keys lexicographically.
            - inner: use intersection of keys from both frames,
              similar to a SQL inner join; preserve the order of the left keys.
        on : label or list
            Column or index level names to join on.
            These must be found in both DataFrames. If on is None and not merging on indexes
            then this defaults to the intersection of the columns in both DataFrames.
        left_on : label or list, or array-like
            Column or index level names to join on in the left DataFrame.
            Can also be an array or list of arrays of the length of the left DataFrame.
            These arrays are treated as if they are columns.
        right_on : label or list, or array-like
            Column or index level names to join on in the right DataFrame.
            Can also be an array or list of arrays of the length of the right DataFrame.
            These arrays are treated as if they are columns.
        left_index : bool, default False
            Use the index from the left DataFrame as the join key(s).
            If it is a MultiIndex, the number of keys in the other DataFrame
            (either the index or a number of columns) must match the number of levels.
        right_index : bool, default False
            Use the index from the right DataFrame as the join key. Same caveats as left_index.
        sort : bool, default False
            Sort the join keys lexicographically in the result DataFrame.
            If False, the order of the join keys depends on the join type (how keyword).
        suffixes : tuple of (str, str), default ('_x', '_y')
            Suffix to apply to overlapping column names in the left and right side, respectively.
            To raise an exception on overlapping columns use (False, False).
        copy : bool, default True
            If False, avoid copy if possible.
        indicator : bool or str, default False
            If True, adds a column to output DataFrame called "_merge" with information
            on the source of each row. If string, column with information on source of each row
            will be added to output DataFrame, and column will be named value of string.
            Information column is Categorical-type and takes on a value of "left_only"
            for observations whose merge key only appears in 'left' DataFrame,
            "right_only" for observations whose merge key only appears in 'right' DataFrame,
            and "both" if the observation’s merge key is found in both.
        validate : str, optional
            If specified, checks if merge is of specified type.
            - 'one_to_one' or '1:1': check if merge keys are unique in both left and right datasets.
            - 'one_to_many' or '1:m': check if merge keys are unique in left dataset.
            - 'many_to_one' or 'm:1': check if merge keys are unique in right dataset.
            - 'many_to_many' or 'm:m': allowed, but does not result in checks.

        Returns
        -------
        DataFrame
             A DataFrame of the two merged objects.
        """
        if isinstance(right, Series):
            if right.name is None:
                raise ValueError("Cannot merge a Series without a name")
            else:
                right = right.to_frame()
        if not isinstance(right, DataFrame):
            raise TypeError(
                f"Can only merge Series or DataFrame objects, a {type(right)} was passed"
            )

        if left_index and right_index:
            return self.join(
                right, how=how, lsuffix=suffixes[0], rsuffix=suffixes[1], sort=sort
            )

        return self.__constructor__(
            query_compiler=self._query_compiler.merge(
                right._query_compiler,
                how=how,
                on=on,
                left_on=left_on,
                right_on=right_on,
                left_index=left_index,
                right_index=right_index,
                sort=sort,
                suffixes=suffixes,
                copy=copy,
                indicator=indicator,
                validate=validate,
            )
        )