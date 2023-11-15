    def to_stata(self, fname, convert_dates=None, write_index=True,
                 encoding="latin-1", byteorder=None, time_stamp=None,
                 data_label=None, variable_labels=None):
        """
        A class for writing Stata binary dta files from array-like objects

        Parameters
        ----------
        fname : str or buffer
            String path of file-like object
        convert_dates : dict
            Dictionary mapping columns containing datetime types to stata
            internal format to use when writing the dates. Options are 'tc',
            'td', 'tm', 'tw', 'th', 'tq', 'ty'. Column can be either an integer
            or a name. Datetime columns that do not have a conversion type
            specified will be converted to 'tc'. Raises NotImplementedError if
            a datetime column has timezone information
        write_index : bool
            Write the index to Stata dataset.
        encoding : str
            Default is latin-1. Unicode is not supported
        byteorder : str
            Can be ">", "<", "little", or "big". default is `sys.byteorder`
        time_stamp : datetime
            A datetime to use as file creation date.  Default is the current
            time.
        data_label : str
            A label for the data set.  Must be 80 characters or smaller.
        variable_labels : dict
            Dictionary containing columns as keys and variable labels as
            values. Each label must be 80 characters or smaller.

            .. versionadded:: 0.19.0

        Raises
        ------
        NotImplementedError
            * If datetimes contain timezone information
            * Column dtype is not representable in Stata
        ValueError
            * Columns listed in convert_dates are neither datetime64[ns]
              or datetime.datetime
            * Column listed in convert_dates is not in DataFrame
            * Categorical label contains more than 32,000 characters

            .. versionadded:: 0.19.0

        Examples
        --------
        >>> data.to_stata('./data_file.dta')

        Or with dates

        >>> data.to_stata('./date_data_file.dta', {2 : 'tw'})

        Alternatively you can create an instance of the StataWriter class

        >>> writer = StataWriter('./data_file.dta', data)
        >>> writer.write_file()

        With dates:

        >>> writer = StataWriter('./date_data_file.dta', data, {2 : 'tw'})
        >>> writer.write_file()
        """
        from pandas.io.stata import StataWriter
        writer = StataWriter(fname, self, convert_dates=convert_dates,
                             encoding=encoding, byteorder=byteorder,
                             time_stamp=time_stamp, data_label=data_label,
                             write_index=write_index,
                             variable_labels=variable_labels)
        writer.write_file()