    def astype(self, dtype) -> 'DataFrame':
        """
        Cast a pandas object to a specified dtype ``dtype``.

        Parameters
        ----------
        dtype : data type, or dict of column name -> data type
            Use a numpy.dtype or Python type to cast entire pandas object to
            the same type. Alternatively, use {col: dtype, ...}, where col is a
            column label and dtype is a numpy.dtype or Python type to cast one
            or more of the DataFrame's columns to column-specific types.

        Returns
        -------
        casted : same type as caller

        See Also
        --------
        to_datetime : Convert argument to datetime.

        Examples
        --------
        >>> df = ks.DataFrame({'a': [1, 2, 3], 'b': [1, 2, 3]}, dtype='int64')
        >>> df
           a  b
        0  1  1
        1  2  2
        2  3  3

        Convert to float type:

        >>> df.astype('float')
             a    b
        0  1.0  1.0
        1  2.0  2.0
        2  3.0  3.0

        Convert to int64 type back:

        >>> df.astype('int64')
           a  b
        0  1  1
        1  2  2
        2  3  3

        Convert column a to float type:

        >>> df.astype({'a': float})
             a  b
        0  1.0  1
        1  2.0  2
        2  3.0  3

        """
        results = []
        if is_dict_like(dtype):
            for col_name in dtype.keys():
                if col_name not in self.columns:
                    raise KeyError('Only a column name can be used for the '
                                   'key in a dtype mappings argument.')
            for col_name, col in self.iteritems():
                if col_name in dtype:
                    results.append(col.astype(dtype=dtype[col_name]))
                else:
                    results.append(col)
        else:
            for col_name, col in self.iteritems():
                results.append(col.astype(dtype=dtype))
        sdf = self._sdf.select(
            self._internal.index_columns + list(map(lambda ser: ser._scol, results)))
        return DataFrame(self._internal.copy(sdf=sdf))