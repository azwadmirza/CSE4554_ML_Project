    def transpose(self, limit: Optional[int] = 1000):
        """
        Transpose index and columns.

        Reflect the DataFrame over its main diagonal by writing rows as columns
        and vice-versa. The property :attr:`.T` is an accessor to the method
        :meth:`transpose`.

        .. note:: This method is based on an expensive operation due to the nature
            of big data. Internally it needs to generate each row for each value, and
            then group twice - it is a huge operation. To prevent misusage, this method
            has the default limit of input length, 1000 and raises a ValueError.

                >>> ks.DataFrame({'a': range(1001)}).transpose()  # doctest: +NORMALIZE_WHITESPACE
                Traceback (most recent call last):
                  ...
                ValueError: Current DataFrame has more then the given limit 1000 rows.
                Please use df.transpose(limit=<maximum number of rows>) to retrieve more than
                1000 rows. Note that, before changing the given 'limit', this operation is
                considerably expensive.

        Parameters
        ----------
        limit : int, optional
            This parameter sets the limit of the current DataFrame. Set `None` to unlimit
            the input length. When the limit is set, it is executed by the shortcut by collecting
            the data into driver side, and then using pandas API. If the limit is unset,
            the operation is executed by PySpark. Default is 1000.

        Returns
        -------
        DataFrame
            The transposed DataFrame.

        Notes
        -----
        Transposing a DataFrame with mixed dtypes will result in a homogeneous
        DataFrame with the coerced dtype. For instance, if int and float have
        to be placed in same column, it becomes float. If type coercion is not
        possible, it fails.

        Also, note that the values in index should be unique because they become
        unique column names.

        In addition, if Spark 2.3 is used, the types should always be exactly same.

        Examples
        --------
        **Square DataFrame with homogeneous dtype**

        >>> d1 = {'col1': [1, 2], 'col2': [3, 4]}
        >>> df1 = ks.DataFrame(data=d1, columns=['col1', 'col2'])
        >>> df1
           col1  col2
        0     1     3
        1     2     4

        >>> df1_transposed = df1.T.sort_index()  # doctest: +SKIP
        >>> df1_transposed  # doctest: +SKIP
              0  1
        col1  1  2
        col2  3  4

        When the dtype is homogeneous in the original DataFrame, we get a
        transposed DataFrame with the same dtype:

        >>> df1.dtypes
        col1    int64
        col2    int64
        dtype: object
        >>> df1_transposed.dtypes  # doctest: +SKIP
        0    int64
        1    int64
        dtype: object

        **Non-square DataFrame with mixed dtypes**

        >>> d2 = {'score': [9.5, 8],
        ...       'kids': [0, 0],
        ...       'age': [12, 22]}
        >>> df2 = ks.DataFrame(data=d2, columns=['score', 'kids', 'age'])
        >>> df2
           score  kids  age
        0    9.5     0   12
        1    8.0     0   22

        >>> df2_transposed = df2.T.sort_index()  # doctest: +SKIP
        >>> df2_transposed  # doctest: +SKIP
                  0     1
        age    12.0  22.0
        kids    0.0   0.0
        score   9.5   8.0

        When the DataFrame has mixed dtypes, we get a transposed DataFrame with
        the coerced dtype:

        >>> df2.dtypes
        score    float64
        kids       int64
        age        int64
        dtype: object

        >>> df2_transposed.dtypes  # doctest: +SKIP
        0    float64
        1    float64
        dtype: object
        """
        if len(self._internal.index_columns) != 1:
            raise ValueError("Single index must be set to transpose the current DataFrame.")
        if limit is not None:
            pdf = self.head(limit + 1).to_pandas()
            if len(pdf) > limit:
                raise ValueError(
                    "Current DataFrame has more then the given limit %s rows. Please use "
                    "df.transpose(limit=<maximum number of rows>) to retrieve more than %s rows. "
                    "Note that, before changing the given 'limit', this operation is considerably "
                    "expensive." % (limit, limit))
            return DataFrame(pdf.transpose())

        index_columns = self._internal.index_columns
        index_column = index_columns[0]
        data_columns = self._internal.data_columns
        sdf = self._sdf

        # Explode the data to be pairs.
        #
        # For instance, if the current input DataFrame is as below:
        #
        # +-----+---+---+---+
        # |index| x1| x2| x3|
        # +-----+---+---+---+
        # |   y1|  1|  0|  0|
        # |   y2|  0| 50|  0|
        # |   y3|  3|  2|  1|
        # +-----+---+---+---+
        #
        # Output of `exploded_df` becomes as below:
        #
        # +-----+---+-----+
        # |index|key|value|
        # +-----+---+-----+
        # |   y1| x1|    1|
        # |   y1| x2|    0|
        # |   y1| x3|    0|
        # |   y2| x1|    0|
        # |   y2| x2|   50|
        # |   y2| x3|    0|
        # |   y3| x1|    3|
        # |   y3| x2|    2|
        # |   y3| x3|    1|
        # +-----+---+-----+
        pairs = F.explode(F.array(*[
            F.struct(
                F.lit(column).alias("key"),
                scol_for(sdf, column).alias("value")
            ) for column in data_columns]))

        exploded_df = sdf.withColumn("pairs", pairs).select(
            [scol_for(sdf, index_column), F.col("pairs.key"), F.col("pairs.value")])

        # After that, executes pivot with key and its index column.
        # Note that index column should contain unique values since column names
        # should be unique.
        pivoted_df = exploded_df.groupBy(F.col("key")).pivot('`{}`'.format(index_column))

        # New index column is always single index.
        internal_index_column = "__index_level_0__"
        transposed_df = pivoted_df.agg(
            F.first(F.col("value"))).withColumnRenamed("key", internal_index_column)

        new_data_columns = filter(lambda x: x != internal_index_column, transposed_df.columns)

        internal = self._internal.copy(
            sdf=transposed_df,
            data_columns=list(new_data_columns),
            index_map=[(internal_index_column, None)])

        return DataFrame(internal)