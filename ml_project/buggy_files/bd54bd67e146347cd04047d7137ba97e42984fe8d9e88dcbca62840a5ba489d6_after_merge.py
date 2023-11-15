    def __init__(
        self,
        partitions,
        index,
        columns,
        row_lengths=None,
        column_widths=None,
        dtypes=None,
        validate_axes: Union[bool, str] = False,
    ):
        """Initialize a dataframe.

        Parameters
        ----------
            partitions : A 2D NumPy array of partitions. Must contain partition objects.
            index : The index object for the dataframe. Converts to a pandas.Index.
            columns : The columns object for the dataframe. Converts to a pandas.Index.
            row_lengths : (optional) The lengths of each partition in the rows. The
                "height" of each of the block partitions. Is computed if not provided.
            column_widths : (optional) The width of each partition in the columns. The
                "width" of each of the block partitions. Is computed if not provided.
            dtypes : (optional) The data types for the dataframe.
            validate_axes : (optional) Whether or not validate for equality
                internal indices of partitions and passed `index` and `columns`.
        """
        self._partitions = partitions
        self._index_cache = ensure_index(index)
        self._columns_cache = ensure_index(columns)
        if row_lengths is not None and len(self.index) > 0:
            ErrorMessage.catch_bugs_and_request_email(
                sum(row_lengths) != len(self._index_cache),
                "Row lengths: {} != {}".format(
                    sum(row_lengths), len(self._index_cache)
                ),
            )
        self._row_lengths_cache = row_lengths
        if column_widths is not None and len(self.columns) > 0:
            ErrorMessage.catch_bugs_and_request_email(
                sum(column_widths) != len(self._columns_cache),
                "Column widths: {} != {}".format(
                    sum(column_widths), len(self._columns_cache)
                ),
            )
        self._column_widths_cache = column_widths
        self._dtypes = dtypes
        self._filter_empties()
        if validate_axes is not False:
            self._validate_internal_indices(mode=validate_axes)