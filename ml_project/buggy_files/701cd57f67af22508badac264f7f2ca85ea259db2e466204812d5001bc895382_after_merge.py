    def __init__(self, f: Union[FilePathOrBuffer, List], **kwds):
        """
        Workhorse function for processing nested list into DataFrame
        """
        ParserBase.__init__(self, kwds)

        self.data: Optional[Iterator[str]] = None
        self.buf: List = []
        self.pos = 0
        self.line_pos = 0

        self.skiprows = kwds["skiprows"]

        if callable(self.skiprows):
            self.skipfunc = self.skiprows
        else:
            self.skipfunc = lambda x: x in self.skiprows

        self.skipfooter = _validate_skipfooter_arg(kwds["skipfooter"])
        self.delimiter = kwds["delimiter"]

        self.quotechar = kwds["quotechar"]
        if isinstance(self.quotechar, str):
            self.quotechar = str(self.quotechar)

        self.escapechar = kwds["escapechar"]
        self.doublequote = kwds["doublequote"]
        self.skipinitialspace = kwds["skipinitialspace"]
        self.lineterminator = kwds["lineterminator"]
        self.quoting = kwds["quoting"]
        self.usecols, _ = _validate_usecols_arg(kwds["usecols"])
        self.skip_blank_lines = kwds["skip_blank_lines"]

        self.warn_bad_lines = kwds["warn_bad_lines"]
        self.error_bad_lines = kwds["error_bad_lines"]

        self.names_passed = kwds["names"] or None

        self.has_index_names = False
        if "has_index_names" in kwds:
            self.has_index_names = kwds["has_index_names"]

        self.verbose = kwds["verbose"]
        self.converters = kwds["converters"]

        self.dtype = kwds["dtype"]
        self.thousands = kwds["thousands"]
        self.decimal = kwds["decimal"]

        self.comment = kwds["comment"]

        # Set self.data to something that can read lines.
        if isinstance(f, list):
            # read_excel: f is a list
            self.data = cast(Iterator[str], f)
        else:
            self._open_handles(f, kwds)
            assert self.handles is not None
            assert hasattr(self.handles.handle, "readline")
            try:
                self._make_reader(self.handles.handle)
            except (csv.Error, UnicodeDecodeError):
                self.close()
                raise

        # Get columns in two steps: infer from data, then
        # infer column indices from self.usecols if it is specified.
        self._col_indices: Optional[List[int]] = None
        try:
            (
                self.columns,
                self.num_original_columns,
                self.unnamed_cols,
            ) = self._infer_columns()
        except (TypeError, ValueError):
            self.close()
            raise

        # Now self.columns has the set of columns that we will process.
        # The original set is stored in self.original_columns.
        if len(self.columns) > 1:
            # we are processing a multi index column
            (
                self.columns,
                self.index_names,
                self.col_names,
                _,
            ) = self._extract_multi_indexer_columns(
                self.columns, self.index_names, self.col_names
            )
            # Update list of original names to include all indices.
            self.num_original_columns = len(self.columns)
        else:
            self.columns = self.columns[0]

        # get popped off for index
        self.orig_names = list(self.columns)

        # needs to be cleaned/refactored
        # multiple date column thing turning into a real spaghetti factory

        if not self._has_complex_date_col:
            (index_names, self.orig_names, self.columns) = self._get_index_name(
                self.columns
            )
            self._name_processed = True
            if self.index_names is None:
                self.index_names = index_names

        if self._col_indices is None:
            self._col_indices = list(range(len(self.columns)))

        self._validate_parse_dates_presence(self.columns)
        if self.parse_dates:
            self._no_thousands_columns = self._set_no_thousands_columns()
        else:
            self._no_thousands_columns = None

        if len(self.decimal) != 1:
            raise ValueError("Only length-1 decimal markers supported")

        decimal = re.escape(self.decimal)
        if self.thousands is None:
            regex = fr"^[\-\+]?[0-9]*({decimal}[0-9]*)?([0-9]?(E|e)\-?[0-9]+)?$"
        else:
            thousands = re.escape(self.thousands)
            regex = (
                fr"^[\-\+]?([0-9]+{thousands}|[0-9])*({decimal}[0-9]*)?"
                fr"([0-9]?(E|e)\-?[0-9]+)?$"
            )
        self.num = re.compile(regex)