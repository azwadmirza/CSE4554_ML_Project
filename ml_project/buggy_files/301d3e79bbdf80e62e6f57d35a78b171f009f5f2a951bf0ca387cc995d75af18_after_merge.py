    def __init__(self, obj, path_or_buf=None, sep=",", na_rep='', float_format=None,
                 cols=None, header=True, index=True, index_label=None,
                 mode='w', nanRep=None, encoding=None, quoting=None,
                 line_terminator='\n', chunksize=None, engine=None,
                 tupleize_cols=False, quotechar='"', date_format=None,
                 doublequote=True, escapechar=None):

        self.engine = engine  # remove for 0.13
        self.obj = obj

        if path_or_buf is None:
            path_or_buf = StringIO()

        self.path_or_buf = path_or_buf
        self.sep = sep
        self.na_rep = na_rep
        self.float_format = float_format

        self.header = header
        self.index = index
        self.index_label = index_label
        self.mode = mode
        self.encoding = encoding

        if quoting is None:
            quoting = csv.QUOTE_MINIMAL
        self.quoting = quoting

        if quoting == csv.QUOTE_NONE:
            # prevents crash in _csv
            quotechar = None
        self.quotechar = quotechar

        self.doublequote = doublequote
        self.escapechar = escapechar

        self.line_terminator = line_terminator

        self.date_format = date_format

        # GH3457
        if not self.obj.columns.is_unique and engine == 'python':
            raise NotImplementedError("columns.is_unique == False not "
                                      "supported with engine='python'")

        self.tupleize_cols = tupleize_cols
        self.has_mi_columns = isinstance(obj.columns, MultiIndex
                                         ) and not self.tupleize_cols

        # validate mi options
        if self.has_mi_columns:
            if cols is not None:
                raise TypeError("cannot specify cols with a MultiIndex on the "
                                "columns")

        if cols is not None:
            if isinstance(cols, Index):
                cols = cols.to_native_types(na_rep=na_rep,
                                            float_format=float_format,
                                            date_format=date_format)
            else:
                cols = list(cols)
            self.obj = self.obj.loc[:, cols]

        # update columns to include possible multiplicity of dupes
        # and make sure sure cols is just a list of labels
        cols = self.obj.columns
        if isinstance(cols, Index):
            cols = cols.to_native_types(na_rep=na_rep,
                                        float_format=float_format,
                                        date_format=date_format)
        else:
            cols = list(cols)

        # save it
        self.cols = cols

        # preallocate data 2d list
        self.blocks = self.obj._data.blocks
        ncols = sum(b.shape[0] for b in self.blocks)
        self.data = [None] * ncols

        if chunksize is None:
            chunksize = (100000 // (len(self.cols) or 1)) or 1
        self.chunksize = int(chunksize)

        self.data_index = obj.index
        if isinstance(obj.index, PeriodIndex):
            self.data_index = obj.index.to_timestamp()

        if (isinstance(self.data_index, DatetimeIndex) and
                date_format is not None):
            self.data_index = Index([x.strftime(date_format)
                                     if notnull(x) else ''
                                     for x in self.data_index])

        self.nlevels = getattr(self.data_index, 'nlevels', 1)
        if not index:
            self.nlevels = 0