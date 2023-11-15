def dataframe_sort_values(df, by, axis=0, ascending=True, inplace=False, kind='quicksort',
                          na_position='last', ignore_index=False, parallel_kind='PSRS', psrs_kinds=None):
    """
    Sort by the values along either axis.

    Parameters
    ----------
    df : Mars DataFrame
         Input dataframe.
    by : str
         Name or list of names to sort by.
    axis : %(axes_single_arg)s, default 0
         Axis to be sorted.
    ascending : bool or list of bool, default True
         Sort ascending vs. descending. Specify list for multiple sort
         orders.  If this is a list of bools, must match the length of
         the by.
    inplace : bool, default False
         If True, perform operation in-place.
    kind : {'quicksort', 'mergesort', 'heapsort'}, default 'quicksort'
         Choice of sorting algorithm. See also ndarray.np.sort for more
         information.  `mergesort` is the only stable algorithm. For
         DataFrames, this option is only applied when sorting on a single
         column or label.
    na_position : {'first', 'last'}, default 'last'
         Puts NaNs at the beginning if `first`; `last` puts NaNs at the
         end.
    ignore_index : bool, default False
         If True, the resulting axis will be labeled 0, 1, …, n - 1.
    parallel_kind : {'PSRS'}, default 'PSRS'
         Parallel sorting algorithm, for the details, refer to:
         http://csweb.cs.wfu.edu/bigiron/LittleFE-PSRS/build/html/PSRSalgorithm.html

    Returns
    -------
    sorted_obj : DataFrame or None
        DataFrame with sorted values if inplace=False, None otherwise.

    Examples
    --------
    >>> import mars.dataframe as md
    >>> df = md.DataFrame({
    ...     'col1': ['A', 'A', 'B', np.nan, 'D', 'C'],
    ...     'col2': [2, 1, 9, 8, 7, 4],
    ...     'col3': [0, 1, 9, 4, 2, 3],
    ... })
    >>> df.execute()
        col1 col2 col3
    0   A    2    0
    1   A    1    1
    2   B    9    9
    3   NaN  8    4
    4   D    7    2
    5   C    4    3

    Sort by col1

    >>> df.sort_values(by=['col1']).execute()
        col1 col2 col3
    0   A    2    0
    1   A    1    1
    2   B    9    9
    5   C    4    3
    4   D    7    2
    3   NaN  8    4

    Sort by multiple columns

    >>> df.sort_values(by=['col1', 'col2']).execute()
        col1 col2 col3
    1   A    1    1
    0   A    2    0
    2   B    9    9
    5   C    4    3
    4   D    7    2
    3   NaN  8    4

    Sort Descending

    >>> df.sort_values(by='col1', ascending=False).execute()
        col1 col2 col3
    4   D    7    2
    5   C    4    3
    2   B    9    9
    0   A    2    0
    1   A    1    1
    3   NaN  8    4

    Putting NAs first

    >>> df.sort_values(by='col1', ascending=False, na_position='first').execute()
        col1 col2 col3
    3   NaN  8    4
    4   D    7    2
    5   C    4    3
    2   B    9    9
    0   A    2    0
    1   A    1    1
    """

    if na_position not in ['last', 'first']:  # pragma: no cover
        raise TypeError(f'invalid na_position: {na_position}')
    axis = validate_axis(axis, df)
    if axis != 0:
        raise NotImplementedError('Only support sort on axis 0')
    psrs_kinds = _validate_sort_psrs_kinds(psrs_kinds)
    by = by if isinstance(by, (list, tuple)) else [by]
    op = DataFrameSortValues(by=by, axis=axis, ascending=ascending, inplace=inplace, kind=kind,
                             na_position=na_position, ignore_index=ignore_index, parallel_kind=parallel_kind,
                             psrs_kinds=psrs_kinds, output_types=[OutputType.dataframe])
    sorted_df = op(df)
    if inplace:
        df.data = sorted_df.data
    else:
        return sorted_df