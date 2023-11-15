    def rank(self, method='average', ascending=True):
        """
        Compute numerical data ranks (1 through n) along axis. Equal values are
        assigned a rank that is the average of the ranks of those values.

        .. note:: the current implementation of rank uses Spark's Window without
            specifying partition specification. This leads to move all data into
            single partition in single machine and could cause serious
            performance degradation. Avoid this method against very large dataset.

        Parameters
        ----------
        method : {'average', 'min', 'max', 'first', 'dense'}
            * average: average rank of group
            * min: lowest rank in group
            * max: highest rank in group
            * first: ranks assigned in order they appear in the array
            * dense: like 'min', but rank always increases by 1 between groups
        ascending : boolean, default True
            False for ranks by high (1) to low (N)

        Returns
        -------
        ranks : same type as caller

        Examples
        --------
        >>> df = ks.DataFrame({'A': [1, 2, 2, 3], 'B': [4, 3, 2, 1]}, columns= ['A', 'B'])
        >>> df
           A  B
        0  1  4
        1  2  3
        2  2  2
        3  3  1

        >>> df.rank().sort_index()
             A    B
        0  1.0  4.0
        1  2.5  3.0
        2  2.5  2.0
        3  4.0  1.0

        If method is set to 'min', it use lowest rank in group.

        >>> df.rank(method='min').sort_index()
             A    B
        0  1.0  4.0
        1  2.0  3.0
        2  2.0  2.0
        3  4.0  1.0

        If method is set to 'max', it use highest rank in group.

        >>> df.rank(method='max').sort_index()
             A    B
        0  1.0  4.0
        1  3.0  3.0
        2  3.0  2.0
        3  4.0  1.0

        If method is set to 'dense', it leaves no gaps in group.

        >>> df.rank(method='dense').sort_index()
             A    B
        0  1.0  4.0
        1  2.0  3.0
        2  2.0  2.0
        3  3.0  1.0
        """
        if method not in ['average', 'min', 'max', 'first', 'dense']:
            msg = "method must be one of 'average', 'min', 'max', 'first', 'dense'"
            raise ValueError(msg)

        if ascending:
            asc_func = lambda sdf, column_name: scol_for(sdf, column_name).asc()
        else:
            asc_func = lambda sdf, column_name: scol_for(sdf, column_name).desc()

        index_column = self._internal.index_columns[0]
        data_columns = self._internal.data_columns
        sdf = self._sdf

        for column_name in data_columns:
            if method == 'first':
                window = Window.orderBy(asc_func(sdf, column_name), asc_func(sdf, index_column))\
                    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
                sdf = sdf.withColumn(column_name, F.row_number().over(window))
            elif method == 'dense':
                window = Window.orderBy(asc_func(sdf, column_name))\
                    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
                sdf = sdf.withColumn(column_name, F.dense_rank().over(window))
            else:
                if method == 'average':
                    stat_func = F.mean
                elif method == 'min':
                    stat_func = F.min
                elif method == 'max':
                    stat_func = F.max
                window = Window.orderBy(asc_func(sdf, column_name))\
                    .rowsBetween(Window.unboundedPreceding, Window.currentRow)
                sdf = sdf.withColumn('rank', F.row_number().over(window))
                window = Window.partitionBy(scol_for(sdf, column_name))\
                    .rowsBetween(Window.unboundedPreceding, Window.unboundedFollowing)
                sdf = sdf.withColumn(column_name, stat_func(F.col('rank')).over(window))

        return DataFrame(self._internal.copy(sdf=sdf.select([scol_for(sdf, col)
                                                             for col in self._internal.columns])))\
            .astype(np.float64)