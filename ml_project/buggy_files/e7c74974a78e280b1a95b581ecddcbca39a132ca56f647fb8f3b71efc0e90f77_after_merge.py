    def _infer_columns(self):
        names = self.names
        num_original_columns = 0
        clear_buffer = True
        if self.header is not None:
            header = self.header

            # we have a mi columns, so read an extra line
            if isinstance(header, (list, tuple, np.ndarray)):
                have_mi_columns = True
                header = list(header) + [header[-1] + 1]
            else:
                have_mi_columns = False
                header = [header]

            columns = []
            for level, hr in enumerate(header):
                try:
                    line = self._buffered_line()

                    while self.line_pos <= hr:
                        line = self._next_line()

                except StopIteration:
                    if self.line_pos < hr:
                        raise ValueError(
                            'Passed header=%s but only %d lines in file'
                            % (hr, self.line_pos + 1))

                    # We have an empty file, so check
                    # if columns are provided. That will
                    # serve as the 'line' for parsing
                    if have_mi_columns and hr > 0:
                        if clear_buffer:
                            self._clear_buffer()
                        columns.append([None] * len(columns[-1]))
                        return columns, num_original_columns

                    if not self.names:
                        raise EmptyDataError(
                            "No columns to parse from file")

                    line = self.names[:]

                unnamed_count = 0
                this_columns = []
                for i, c in enumerate(line):
                    if c == '':
                        if have_mi_columns:
                            this_columns.append('Unnamed: %d_level_%d'
                                                % (i, level))
                        else:
                            this_columns.append('Unnamed: %d' % i)
                        unnamed_count += 1
                    else:
                        this_columns.append(c)

                if not have_mi_columns and self.mangle_dupe_cols:
                    counts = {}
                    for i, col in enumerate(this_columns):
                        cur_count = counts.get(col, 0)
                        if cur_count > 0:
                            this_columns[i] = '%s.%d' % (col, cur_count)
                        counts[col] = cur_count + 1
                elif have_mi_columns:

                    # if we have grabbed an extra line, but its not in our
                    # format so save in the buffer, and create an blank extra
                    # line for the rest of the parsing code
                    if hr == header[-1]:
                        lc = len(this_columns)
                        ic = (len(self.index_col)
                              if self.index_col is not None else 0)
                        if lc != unnamed_count and lc - ic > unnamed_count:
                            clear_buffer = False
                            this_columns = [None] * lc
                            self.buf = [self.buf[-1]]

                columns.append(this_columns)
                if len(columns) == 1:
                    num_original_columns = len(this_columns)

            if clear_buffer:
                self._clear_buffer()

            if names is not None:
                if ((self.usecols is not None and
                     len(names) != len(self.usecols)) or
                    (self.usecols is None and
                     len(names) != len(columns[0]))):
                    raise ValueError('Number of passed names did not match '
                                     'number of header fields in the file')
                if len(columns) > 1:
                    raise TypeError('Cannot pass names with multi-index '
                                    'columns')

                if self.usecols is not None:
                    # Set _use_cols. We don't store columns because they are
                    # overwritten.
                    self._handle_usecols(columns, names)
                else:
                    self._col_indices = None
                    num_original_columns = len(names)
                columns = [names]
            else:
                columns = self._handle_usecols(columns, columns[0])
        else:
            try:
                line = self._buffered_line()

            except StopIteration:
                if not names:
                    raise EmptyDataError(
                        "No columns to parse from file")

                line = names[:]

            ncols = len(line)
            num_original_columns = ncols

            if not names:
                if self.prefix:
                    columns = [['%s%d' % (self.prefix, i)
                                for i in range(ncols)]]
                else:
                    columns = [lrange(ncols)]
                columns = self._handle_usecols(columns, columns[0])
            else:
                if self.usecols is None or len(names) >= num_original_columns:
                    columns = self._handle_usecols([names], names)
                    num_original_columns = len(names)
                else:
                    if (not callable(self.usecols) and
                            len(names) != len(self.usecols)):
                        raise ValueError(
                            'Number of passed names did not match number of '
                            'header fields in the file'
                        )
                    # Ignore output but set used columns.
                    self._handle_usecols([names], names)
                    columns = [names]
                    num_original_columns = ncols

        return columns, num_original_columns