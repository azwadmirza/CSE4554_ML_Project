    def write_result(self, buf):
        """
        Render a DataFrame to a LaTeX tabular/longtable environment output.
        """

        # string representation of the columns
        if len(self.frame.columns) == 0 or len(self.frame.index) == 0:
            info_line = (u('Empty {name}\nColumns: {col}\nIndex: {idx}')
                         .format(name=type(self.frame).__name__,
                                 col=self.frame.columns,
                                 idx=self.frame.index))
            strcols = [[info_line]]
        else:
            strcols = self.fmt._to_str_columns()

        def get_col_type(dtype):
            if issubclass(dtype.type, np.number):
                return 'r'
            else:
                return 'l'

        # reestablish the MultiIndex that has been joined by _to_str_column
        if self.fmt.index and isinstance(self.frame.index, MultiIndex):
            clevels = self.frame.columns.nlevels
            strcols.pop(0)
            name = any(self.frame.index.names)
            cname = any(self.frame.columns.names)
            lastcol = self.frame.index.nlevels - 1
            previous_lev3 = None
            for i, lev in enumerate(self.frame.index.levels):
                lev2 = lev.format()
                blank = ' ' * len(lev2[0])
                # display column names in last index-column
                if cname and i == lastcol:
                    lev3 = [x if x else '{}' for x in self.frame.columns.names]
                else:
                    lev3 = [blank] * clevels
                if name:
                    lev3.append(lev.name)
                current_idx_val = None
                for level_idx in self.frame.index.labels[i]:
                    if ((previous_lev3 is None or
                        previous_lev3[len(lev3)].isspace()) and
                            lev2[level_idx] == current_idx_val):
                        # same index as above row and left index was the same
                        lev3.append(blank)
                    else:
                        # different value than above or left index different
                        lev3.append(lev2[level_idx])
                        current_idx_val = lev2[level_idx]
                strcols.insert(i, lev3)
                previous_lev3 = lev3

        column_format = self.column_format
        if column_format is None:
            dtypes = self.frame.dtypes._values
            column_format = ''.join(map(get_col_type, dtypes))
            if self.fmt.index:
                index_format = 'l' * self.frame.index.nlevels
                column_format = index_format + column_format
        elif not isinstance(column_format,
                            compat.string_types):  # pragma: no cover
            raise AssertionError('column_format must be str or unicode, '
                                 'not {typ}'.format(typ=type(column_format)))

        if not self.longtable:
            buf.write('\\begin{{tabular}}{{{fmt}}}\n'
                      .format(fmt=column_format))
            buf.write('\\toprule\n')
        else:
            buf.write('\\begin{{longtable}}{{{fmt}}}\n'
                      .format(fmt=column_format))
            buf.write('\\toprule\n')

        ilevels = self.frame.index.nlevels
        clevels = self.frame.columns.nlevels
        nlevels = clevels
        if any(self.frame.index.names):
            nlevels += 1
        strrows = list(zip(*strcols))
        self.clinebuf = []

        for i, row in enumerate(strrows):
            if i == nlevels and self.fmt.header:
                buf.write('\\midrule\n')  # End of header
                if self.longtable:
                    buf.write('\\endhead\n')
                    buf.write('\\midrule\n')
                    buf.write('\\multicolumn{{{n}}}{{r}}{{{{Continued on next '
                              'page}}}} \\\\\n'.format(n=len(row)))
                    buf.write('\\midrule\n')
                    buf.write('\\endfoot\n\n')
                    buf.write('\\bottomrule\n')
                    buf.write('\\endlastfoot\n')
            if self.fmt.kwds.get('escape', True):
                # escape backslashes first
                crow = [(x.replace('\\', '\\textbackslash').replace('_', '\\_')
                         .replace('%', '\\%').replace('$', '\\$')
                         .replace('#', '\\#').replace('{', '\\{')
                         .replace('}', '\\}').replace('~', '\\textasciitilde')
                         .replace('^', '\\textasciicircum').replace('&', '\\&')
                         if (x and x != '{}') else '{}') for x in row]
            else:
                crow = [x if x else '{}' for x in row]
            if self.bold_rows and self.fmt.index:
                # bold row labels
                crow = ['\\textbf{{{x}}}'.format(x=x)
                        if j < ilevels and x.strip() not in ['', '{}'] else x
                        for j, x in enumerate(crow)]
            if i < clevels and self.fmt.header and self.multicolumn:
                # sum up columns to multicolumns
                crow = self._format_multicolumn(crow, ilevels)
            if (i >= nlevels and self.fmt.index and self.multirow and
                    ilevels > 1):
                # sum up rows to multirows
                crow = self._format_multirow(crow, ilevels, i, strrows)
            buf.write(' & '.join(crow))
            buf.write(' \\\\\n')
            if self.multirow and i < len(strrows) - 1:
                self._print_cline(buf, i, len(strcols))

        if not self.longtable:
            buf.write('\\bottomrule\n')
            buf.write('\\end{tabular}\n')
        else:
            buf.write('\\end{longtable}\n')