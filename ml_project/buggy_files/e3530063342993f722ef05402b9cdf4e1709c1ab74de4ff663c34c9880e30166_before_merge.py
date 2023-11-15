    def _get_lines(self, rows=None):
        source = self.data
        lines = self.buf
        new_rows = None

        # already fetched some number
        if rows is not None:
            # we already have the lines in the buffer
            if len(self.buf) >= rows:
                new_rows, self.buf = self.buf[:rows], self.buf[rows:]

            # need some lines
            else:
                rows -= len(self.buf)

        if new_rows is None:
            if isinstance(source, list):
                if self.pos > len(source):
                    raise StopIteration
                if rows is None:
                    new_rows = source[self.pos:]
                    new_pos = len(source)
                else:
                    new_rows = source[self.pos:self.pos + rows]
                    new_pos = self.pos + rows

                # Check for stop rows. n.b.: self.skiprows is a set.
                if self.skiprows:
                    new_rows = [row for i, row in enumerate(new_rows)
                                if not self.skipfunc(i + self.pos)]

                lines.extend(new_rows)
                self.pos = new_pos

            else:
                new_rows = []
                try:
                    if rows is not None:
                        for _ in range(rows):
                            new_rows.append(next(source))
                        lines.extend(new_rows)
                    else:
                        rows = 0
                        while True:
                            try:
                                new_rows.append(next(source))
                                rows += 1
                            except csv.Error as inst:
                                if 'newline inside string' in str(inst):
                                    row_num = str(self.pos + rows)
                                    msg = ('EOF inside string starting with '
                                           'line ' + row_num)
                                    raise Exception(msg)
                                raise
                except StopIteration:
                    if self.skiprows:
                        new_rows = [row for i, row in enumerate(new_rows)
                                    if not self.skipfunc(i + self.pos)]
                    lines.extend(new_rows)
                    if len(lines) == 0:
                        raise
                self.pos += len(new_rows)

            self.buf = []
        else:
            lines = new_rows

        if self.skipfooter:
            lines = lines[:-self.skipfooter]

        lines = self._check_comments(lines)
        if self.skip_blank_lines:
            lines = self._check_empty(lines)
        lines = self._check_thousands(lines)
        return self._check_decimal(lines)