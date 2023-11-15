    def _from_table(t):
        """
        Extract the data, metadata and units from an astropy table for use in
        constructing a TimeSeries.

        Parameters
        ----------
        t: `~astropy.table.table.Table`
            The input table. The datetime column must be the first column or the
            (single) primary key index.

        Returns
        -------
        data : `~pandas.core.frame.DataFrame`
        meta : `~sunpy.util.metadata.MetaDict`
        units : `dict`
        """
        table = copy.deepcopy(t)
        # Default the time index to the first column
        index_name = table.colnames[0]
        # Check if another column is defined as the index/primary_key
        if table.primary_key:
            # Check there is only one primary_key/index column
            if len(table.primary_key) != 1:
                raise ValueError("Invalid input Table, TimeSeries doesn't support conversion"
                                 " of tables with more then one index column.")

        # Extract, convert and remove the index column from the input table
        index = table[index_name]
        # Convert if the index is given as an astropy Time object
        if isinstance(index, Time):
            index = index.datetime
        index = pd.to_datetime(index)
        table.remove_column(index_name)

        # Extract the column values from the table
        data = {}
        units = {}
        for colname in table.colnames:
            data[colname] = table[colname]
            units[colname] = table[colname].unit

        # Create a dataframe with this and return
        df = pd.DataFrame(data=data, index=index)
        return df, MetaDict(table.meta), units