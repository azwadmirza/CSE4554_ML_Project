    def __init__(self, src, **kwds):
        self.kwds = kwds
        kwds = kwds.copy()

        ParserBase.__init__(self, kwds)

        if (kwds.get('compression') is None
           and 'utf-16' in (kwds.get('encoding') or '')):
            # if source is utf-16 plain text, convert source to utf-8
            if isinstance(src, compat.string_types):
                src = open(src, 'rb')
                self.handles.append(src)
            src = UTF8Recoder(src, kwds['encoding'])
            kwds['encoding'] = 'utf-8'

        # #2442
        kwds['allow_leading_cols'] = self.index_col is not False

        self._reader = parsers.TextReader(src, **kwds)

        # XXX
        self.usecols, self.usecols_dtype = _validate_usecols_arg(
            self._reader.usecols)

        passed_names = self.names is None

        if self._reader.header is None:
            self.names = None
        else:
            if len(self._reader.header) > 1:
                # we have a multi index in the columns
                self.names, self.index_names, self.col_names, passed_names = (
                    self._extract_multi_indexer_columns(
                        self._reader.header, self.index_names, self.col_names,
                        passed_names
                    )
                )
            else:
                self.names = list(self._reader.header[0])

        if self.names is None:
            if self.prefix:
                self.names = ['%s%d' % (self.prefix, i)
                              for i in range(self._reader.table_width)]
            else:
                self.names = lrange(self._reader.table_width)

        # gh-9755
        #
        # need to set orig_names here first
        # so that proper indexing can be done
        # with _set_noconvert_columns
        #
        # once names has been filtered, we will
        # then set orig_names again to names
        self.orig_names = self.names[:]

        if self.usecols:
            usecols = _evaluate_usecols(self.usecols, self.orig_names)

            # GH 14671
            if (self.usecols_dtype == 'string' and
                    not set(usecols).issubset(self.orig_names)):
                raise ValueError("Usecols do not match names.")

            if len(self.names) > len(usecols):
                self.names = [n for i, n in enumerate(self.names)
                              if (i in usecols or n in usecols)]

            if len(self.names) < len(usecols):
                raise ValueError("Usecols do not match names.")

        self._set_noconvert_columns()

        self.orig_names = self.names

        if not self._has_complex_date_col:
            if (self._reader.leading_cols == 0 and
                    _is_index_col(self.index_col)):

                self._name_processed = True
                (index_names, self.names,
                 self.index_col) = _clean_index_names(self.names,
                                                      self.index_col)

                if self.index_names is None:
                    self.index_names = index_names

            if self._reader.header is None and not passed_names:
                self.index_names = [None] * len(self.index_names)

        self._implicit_index = self._reader.leading_cols > 0