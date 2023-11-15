    def to_csv(
        self,
        path_or_buf: Optional[FilePathOrBuffer] = None,
        sep: str = ",",
        na_rep: str = "",
        float_format: Optional[str] = None,
        columns: Optional[Sequence[Label]] = None,
        header: Union[bool_t, List[str]] = True,
        index: bool_t = True,
        index_label: Optional[Union[bool_t, str, Sequence[Label]]] = None,
        mode: str = "w",
        encoding: Optional[str] = None,
        compression: Optional[Union[str, Mapping[str, str]]] = "infer",
        quoting: Optional[int] = None,
        quotechar: str = '"',
        line_terminator: Optional[str] = None,
        chunksize: Optional[int] = None,
        date_format: Optional[str] = None,
        doublequote: bool_t = True,
        escapechar: Optional[str] = None,
        decimal: Optional[str] = ".",
    ) -> Optional[str]:
        r"""
        Write object to a comma-separated values (csv) file.

        .. versionchanged:: 0.24.0
            The order of arguments for Series was changed.

        Parameters
        ----------
        path_or_buf : str or file handle, default None
            File path or object, if None is provided the result is returned as
            a string.  If a file object is passed it should be opened with
            `newline=''`, disabling universal newlines.

            .. versionchanged:: 0.24.0

               Was previously named "path" for Series.

        sep : str, default ','
            String of length 1. Field delimiter for the output file.
        na_rep : str, default ''
            Missing data representation.
        float_format : str, default None
            Format string for floating point numbers.
        columns : sequence, optional
            Columns to write.
        header : bool or list of str, default True
            Write out the column names. If a list of strings is given it is
            assumed to be aliases for the column names.

            .. versionchanged:: 0.24.0

               Previously defaulted to False for Series.

        index : bool, default True
            Write row names (index).
        index_label : str or sequence, or False, default None
            Column label for index column(s) if desired. If None is given, and
            `header` and `index` are True, then the index names are used. A
            sequence should be given if the object uses MultiIndex. If
            False do not print fields for index names. Use index_label=False
            for easier importing in R.
        mode : str
            Python write mode, default 'w'.
        encoding : str, optional
            A string representing the encoding to use in the output file,
            defaults to 'utf-8'.
        compression : str or dict, default 'infer'
            If str, represents compression mode. If dict, value at 'method' is
            the compression mode. Compression mode may be any of the following
            possible values: {'infer', 'gzip', 'bz2', 'zip', 'xz', None}. If
            compression mode is 'infer' and `path_or_buf` is path-like, then
            detect compression mode from the following extensions: '.gz',
            '.bz2', '.zip' or '.xz'. (otherwise no compression). If dict given
            and mode is one of {'zip', 'gzip', 'bz2'}, or inferred as
            one of the above, other entries passed as
            additional compression options.

            .. versionchanged:: 1.0.0

               May now be a dict with key 'method' as compression mode
               and other entries as additional compression options if
               compression mode is 'zip'.

            .. versionchanged:: 1.1.0

               Passing compression options as keys in dict is
               supported for compression modes 'gzip' and 'bz2'
               as well as 'zip'.

        quoting : optional constant from csv module
            Defaults to csv.QUOTE_MINIMAL. If you have set a `float_format`
            then floats are converted to strings and thus csv.QUOTE_NONNUMERIC
            will treat them as non-numeric.
        quotechar : str, default '\"'
            String of length 1. Character used to quote fields.
        line_terminator : str, optional
            The newline character or character sequence to use in the output
            file. Defaults to `os.linesep`, which depends on the OS in which
            this method is called ('\n' for linux, '\r\n' for Windows, i.e.).

            .. versionchanged:: 0.24.0
        chunksize : int or None
            Rows to write at a time.
        date_format : str, default None
            Format string for datetime objects.
        doublequote : bool, default True
            Control quoting of `quotechar` inside a field.
        escapechar : str, default None
            String of length 1. Character used to escape `sep` and `quotechar`
            when appropriate.
        decimal : str, default '.'
            Character recognized as decimal separator. E.g. use ',' for
            European data.

        Returns
        -------
        None or str
            If path_or_buf is None, returns the resulting csv format as a
            string. Otherwise returns None.

        See Also
        --------
        read_csv : Load a CSV file into a DataFrame.
        to_excel : Write DataFrame to an Excel file.

        Examples
        --------
        >>> df = pd.DataFrame({'name': ['Raphael', 'Donatello'],
        ...                    'mask': ['red', 'purple'],
        ...                    'weapon': ['sai', 'bo staff']})
        >>> df.to_csv(index=False)
        'name,mask,weapon\nRaphael,red,sai\nDonatello,purple,bo staff\n'

        Create 'out.zip' containing 'out.csv'

        >>> compression_opts = dict(method='zip',
        ...                         archive_name='out.csv')  # doctest: +SKIP
        >>> df.to_csv('out.zip', index=False,
        ...           compression=compression_opts)  # doctest: +SKIP
        """
        df = self if isinstance(self, ABCDataFrame) else self.to_frame()

        from pandas.io.formats.csvs import CSVFormatter

        formatter = CSVFormatter(
            df,
            path_or_buf,
            line_terminator=line_terminator,
            sep=sep,
            encoding=encoding,
            compression=compression,
            quoting=quoting,
            na_rep=na_rep,
            float_format=float_format,
            cols=columns,
            header=header,
            index=index,
            index_label=index_label,
            mode=mode,
            chunksize=chunksize,
            quotechar=quotechar,
            date_format=date_format,
            doublequote=doublequote,
            escapechar=escapechar,
            decimal=decimal,
        )
        formatter.save()

        if path_or_buf is None:
            return formatter.path_or_buf.getvalue()

        return None