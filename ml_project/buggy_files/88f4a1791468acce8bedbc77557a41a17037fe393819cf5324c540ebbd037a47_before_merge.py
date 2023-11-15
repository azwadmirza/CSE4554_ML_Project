    def select_dtypes(self, include=None, exclude=None):
        """
        Return a subset of the DataFrame's columns based on the column dtypes.

        Parameters
        ----------
        include, exclude : scalar or list-like
            A selection of dtypes or strings to be included/excluded. At least
            one of these parameters must be supplied. It also takes Spark SQL
            DDL type strings, for instance, 'string' and 'date'.

        Returns
        -------
        DataFrame
            The subset of the frame including the dtypes in ``include`` and
            excluding the dtypes in ``exclude``.

        Raises
        ------
        ValueError
            * If both of ``include`` and ``exclude`` are empty

                >>> df = pd.DataFrame({'a': [1, 2] * 3,
                ...                    'b': [True, False] * 3,
                ...                    'c': [1.0, 2.0] * 3})
                >>> df.select_dtypes()
                Traceback (most recent call last):
                ...
                ValueError: at least one of include or exclude must be nonempty

            * If ``include`` and ``exclude`` have overlapping elements

                >>> df = pd.DataFrame({'a': [1, 2] * 3,
                ...                    'b': [True, False] * 3,
                ...                    'c': [1.0, 2.0] * 3})
                >>> df.select_dtypes(include='a', exclude='a')
                Traceback (most recent call last):
                ...
                TypeError: string dtypes are not allowed, use 'object' instead

        Notes
        -----
        * To select datetimes, use ``np.datetime64``, ``'datetime'`` or
          ``'datetime64'``

        Examples
        --------
        >>> df = ks.DataFrame({'a': [1, 2] * 3,
        ...                    'b': [True, False] * 3,
        ...                    'c': [1.0, 2.0] * 3,
        ...                    'd': ['a', 'b'] * 3}, columns=['a', 'b', 'c', 'd'])
        >>> df
           a      b    c  d
        0  1   True  1.0  a
        1  2  False  2.0  b
        2  1   True  1.0  a
        3  2  False  2.0  b
        4  1   True  1.0  a
        5  2  False  2.0  b

        >>> df.select_dtypes(include='bool')
               b
        0   True
        1  False
        2   True
        3  False
        4   True
        5  False

        >>> df.select_dtypes(include=['float64'], exclude=['int'])
             c
        0  1.0
        1  2.0
        2  1.0
        3  2.0
        4  1.0
        5  2.0

        >>> df.select_dtypes(exclude=['int'])
               b    c  d
        0   True  1.0  a
        1  False  2.0  b
        2   True  1.0  a
        3  False  2.0  b
        4   True  1.0  a
        5  False  2.0  b

        Spark SQL DDL type strings can be used as well.

        >>> df.select_dtypes(exclude=['string'])
           a      b    c
        0  1   True  1.0
        1  2  False  2.0
        2  1   True  1.0
        3  2  False  2.0
        4  1   True  1.0
        5  2  False  2.0
        """
        from pyspark.sql.types import _parse_datatype_string

        if not is_list_like(include):
            include = (include,) if include is not None else ()
        if not is_list_like(exclude):
            exclude = (exclude,) if exclude is not None else ()

        if not any((include, exclude)):
            raise ValueError('at least one of include or exclude must be '
                             'nonempty')

        # can't both include AND exclude!
        if set(include).intersection(set(exclude)):
            raise ValueError('include and exclude overlap on {inc_ex}'.format(
                inc_ex=set(include).intersection(set(exclude))))

        # Handle Spark types
        columns = []
        include_spark_type = []
        for inc in include:
            try:
                include_spark_type.append(_parse_datatype_string(inc))
            except:
                pass

        exclude_spark_type = []
        for exc in exclude:
            try:
                exclude_spark_type.append(_parse_datatype_string(exc))
            except:
                pass

        # Handle Pandas types
        include_numpy_type = []
        for inc in include:
            try:
                include_numpy_type.append(infer_dtype_from_object(inc))
            except:
                pass

        exclude_numpy_type = []
        for exc in exclude:
            try:
                exclude_numpy_type.append(infer_dtype_from_object(exc))
            except:
                pass

        for col in self._internal.data_columns:
            if len(include) > 0:
                should_include = (
                    infer_dtype_from_object(self[col].dtype.name) in include_numpy_type or
                    self._sdf.schema[col].dataType in include_spark_type)
            else:
                should_include = not (
                    infer_dtype_from_object(self[col].dtype.name) in exclude_numpy_type or
                    self._sdf.schema[col].dataType in exclude_spark_type)

            if should_include:
                columns += col

        return DataFrame(self._internal.copy(
            sdf=self._sdf.select(self._internal.index_columns + columns), data_columns=columns))