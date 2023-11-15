    def _next_line(self):
        if isinstance(self.data, list):
            while self.skipfunc(self.pos):
                self.pos += 1

            while True:
                try:
                    line = self._check_comments([self.data[self.pos]])[0]
                    self.pos += 1
                    # either uncommented or blank to begin with
                    if not self.skip_blank_lines and (self._empty(self.data[
                            self.pos - 1]) or line):
                        break
                    elif self.skip_blank_lines:
                        ret = self._check_empty([line])
                        if ret:
                            line = ret[0]
                            break
                except IndexError:
                    raise StopIteration
        else:
            while self.skipfunc(self.pos):
                self.pos += 1
                next(self.data)

            while True:
                try:
                    orig_line = next(self.data)
                except csv.Error as e:
                    msg = str(e)

                    if 'NULL byte' in str(e):
                        msg = ('NULL byte detected. This byte '
                               'cannot be processed in Python\'s '
                               'native csv library at the moment, '
                               'so please pass in engine=\'c\' instead')

                    if self.skipfooter > 0:
                        reason = ('Error could possibly be due to '
                                  'parsing errors in the skipped footer rows '
                                  '(the skipfooter keyword is only applied '
                                  'after Python\'s csv library has parsed '
                                  'all rows).')
                        msg += '. ' + reason

                    raise csv.Error(msg)
                line = self._check_comments([orig_line])[0]
                self.pos += 1
                if (not self.skip_blank_lines and
                        (self._empty(orig_line) or line)):
                    break
                elif self.skip_blank_lines:
                    ret = self._check_empty([line])
                    if ret:
                        line = ret[0]
                        break

        # This was the first line of the file,
        # which could contain the BOM at the
        # beginning of it.
        if self.pos == 1:
            line = self._check_for_bom(line)

        self.line_pos += 1
        self.buf.append(line)
        return line