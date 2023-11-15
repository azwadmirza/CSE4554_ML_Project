    def __init__(
        self,
        obj,
        path_or_buf: Optional[FilePathOrBuffer[str]] = None,
        sep: str = ",",
        na_rep: str = "",
        float_format: Optional[str] = None,
        cols=None,
        header: Union[bool, Sequence[Hashable]] = True,
        index: bool = True,
        index_label: Optional[Union[bool, Hashable, Sequence[Hashable]]] = None,
        mode: str = "w",
        encoding: Optional[str] = None,
        compression: Union[str, Mapping[str, str], None] = "infer",
        quoting: Optional[int] = None,
        line_terminator="\n",
        chunksize: Optional[int] = None,
        quotechar='"',
        date_format: Optional[str] = None,
        doublequote: bool = True,
        escapechar: Optional[str] = None,
        decimal=".",
    ):
        self.obj = obj

        if path_or_buf is None:
            path_or_buf = StringIO()

        # Extract compression mode as given, if dict
        compression, self.compression_args = get_compression_method(compression)

        self.path_or_buf, _, _, self.should_close = get_filepath_or_buffer(
            path_or_buf, encoding=encoding, compression=compression, mode=mode
        )
        self.sep = sep
        self.na_rep = na_rep
        self.float_format = float_format
        self.decimal = decimal

        self.header = header
        self.index = index
        self.index_label = index_label
        self.mode = mode
        if encoding is None:
            encoding = "utf-8"
        self.encoding = encoding
        self.compression = infer_compression(self.path_or_buf, compression)

        if quoting is None:
            quoting = csvlib.QUOTE_MINIMAL
        self.quoting = quoting

        if quoting == csvlib.QUOTE_NONE:
            # prevents crash in _csv
            quotechar = None
        self.quotechar = quotechar

        self.doublequote = doublequote
        self.escapechar = escapechar

        self.line_terminator = line_terminator or os.linesep

        self.date_format = date_format

        self.has_mi_columns = isinstance(obj.columns, ABCMultiIndex)

        # validate mi options
        if self.has_mi_columns:
            if cols is not None:
                raise TypeError("cannot specify cols with a MultiIndex on the columns")

        if cols is not None:
            if isinstance(cols, ABCIndexClass):
                cols = cols.to_native_types(
                    na_rep=na_rep,
                    float_format=float_format,
                    date_format=date_format,
                    quoting=self.quoting,
                )
            else:
                cols = list(cols)
            self.obj = self.obj.loc[:, cols]

        # update columns to include possible multiplicity of dupes
        # and make sure sure cols is just a list of labels
        cols = self.obj.columns
        if isinstance(cols, ABCIndexClass):
            cols = cols.to_native_types(
                na_rep=na_rep,
                float_format=float_format,
                date_format=date_format,
                quoting=self.quoting,
            )
        else:
            cols = list(cols)

        # save it
        self.cols = cols

        # preallocate data 2d list
        ncols = self.obj.shape[-1]
        self.data = [None] * ncols

        if chunksize is None:
            chunksize = (100000 // (len(self.cols) or 1)) or 1
        self.chunksize = int(chunksize)

        self.data_index = obj.index
        if (
            isinstance(self.data_index, (ABCDatetimeIndex, ABCPeriodIndex))
            and date_format is not None
        ):
            from pandas import Index

            self.data_index = Index(
                [x.strftime(date_format) if notna(x) else "" for x in self.data_index]
            )

        self.nlevels = getattr(self.data_index, "nlevels", 1)
        if not index:
            self.nlevels = 0