    def _get_lines(self, rows=None):
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
            if isinstance(self.data, list):
                if self.pos > len(self.data):
                    raise StopIteration
                if rows is None:
                    new_rows = self.data[self.pos:]
                    new_pos = len(self.data)
                else:
                    new_rows = self.data[self.pos:self.pos + rows]
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
                            new_rows.append(next(self.data))
                        lines.extend(new_rows)
                    else:
                        rows = 0

                        while True:
                            new_row = self._next_iter_line(
                                row_num=self.pos + rows)
                            new_rows.append(new_row)
                            rows += 1

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