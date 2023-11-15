    def astype(self, dtype, copy=True, errors='raise', **kwargs):
        """
        Cast a pandas object to a specified dtype ``dtype``.

        Parameters
        ----------
        dtype : data type, or dict of column name -> data type
            Use a numpy.dtype or Python type to cast entire pandas object to
            the same type. Alternatively, use {col: dtype, ...}, where col is a
            column label and dtype is a numpy.dtype or Python type to cast one
            or more of the DataFrame's columns to column-specific types.
        copy : bool, default True.
            Return a copy when ``copy=True`` (be very careful setting
            ``copy=False`` as changes to values then may propagate to other
            pandas objects).
        errors : {'raise', 'ignore'}, default 'raise'.
            Control raising of exceptions on invalid data for provided dtype.

            - ``raise`` : allow exceptions to be raised
            - ``ignore`` : suppress exceptions. On error return original object

            .. versionadded:: 0.20.0

        raise_on_error : raise on invalid input
            .. deprecated:: 0.20.0
               Use ``errors`` instead
        kwargs : keyword arguments to pass on to the constructor

        Returns
        -------
        casted : same type as caller

        Examples
        --------
        >>> ser = pd.Series([1, 2], dtype='int32')
        >>> ser
        0    1
        1    2
        dtype: int32
        >>> ser.astype('int64')
        0    1
        1    2
        dtype: int64

        Convert to categorical type:

        >>> ser.astype('category')
        0    1
        1    2
        dtype: category
        Categories (2, int64): [1, 2]

        Convert to ordered categorical type with custom ordering:

        >>> ser.astype('category', ordered=True, categories=[2, 1])
        0    1
        1    2
        dtype: category
        Categories (2, int64): [2 < 1]

        Note that using ``copy=False`` and changing data on a new
        pandas object may propagate changes:

        >>> s1 = pd.Series([1,2])
        >>> s2 = s1.astype('int64', copy=False)
        >>> s2[0] = 10
        >>> s1  # note that s1[0] has changed too
        0    10
        1     2
        dtype: int64

        See also
        --------
        pandas.to_datetime : Convert argument to datetime.
        pandas.to_timedelta : Convert argument to timedelta.
        pandas.to_numeric : Convert argument to a numeric type.
        numpy.ndarray.astype : Cast a numpy array to a specified type.
        """
        if is_dict_like(dtype):
            if self.ndim == 1:  # i.e. Series
                if len(dtype) > 1 or self.name not in dtype:
                    raise KeyError('Only the Series name can be used for '
                                   'the key in Series dtype mappings.')
                new_type = dtype[self.name]
                return self.astype(new_type, copy, errors, **kwargs)
            elif self.ndim > 2:
                raise NotImplementedError(
                    'astype() only accepts a dtype arg of type dict when '
                    'invoked on Series and DataFrames. A single dtype must be '
                    'specified when invoked on a Panel.'
                )
            for col_name in dtype.keys():
                if col_name not in self:
                    raise KeyError('Only a column name can be used for the '
                                   'key in a dtype mappings argument.')
            results = []
            for col_name, col in self.iteritems():
                if col_name in dtype:
                    results.append(col.astype(dtype[col_name], copy=copy))
                else:
                    results.append(results.append(col.copy() if copy else col))

        elif is_categorical_dtype(dtype) and self.ndim > 1:
            # GH 18099: columnwise conversion to categorical
            results = (self[col].astype(dtype, copy=copy) for col in self)

        else:
            # else, only a single dtype is given
            new_data = self._data.astype(dtype=dtype, copy=copy, errors=errors,
                                         **kwargs)
            return self._constructor(new_data).__finalize__(self)

        # GH 19920: retain column metadata after concat
        result = pd.concat(results, axis=1, copy=False)
        result.columns = self.columns
        return result