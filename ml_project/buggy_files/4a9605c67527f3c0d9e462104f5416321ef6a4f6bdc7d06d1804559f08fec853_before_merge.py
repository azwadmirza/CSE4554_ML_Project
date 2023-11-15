    def add_fields(self, *fields):
        for rec in fields:
            if isinstance(rec, io.IOBase):
                k = guess_filename(rec, 'unknown')
                self.add_field(k, rec)
                self._has_io = True

            elif len(rec) == 1:
                k = guess_filename(rec[0], 'unknown')
                self.add_field(k, rec[0])
                if isinstance(rec[0], io.IOBase):
                    self._has_io = True

            elif len(rec) == 2:
                k, fp = rec
                fn = guess_filename(fp)
                self.add_field(k, fp, filename=fn)
                if isinstance(fp, io.IOBase):
                    self._has_io = True

            else:
                k, fp, ft = rec
                fn = guess_filename(fp, k)
                self.add_field(k, fp, contenttype=ft, filename=fn)
                self._has_io = True