    def _setitem(self, tag, value, legacy_api):
        basetypes = (Number, bytes, str)
        if bytes is str:
            basetypes += unicode,

        info = TiffTags.lookup(tag)
        values = [value] if isinstance(value, basetypes) else value

        if tag not in self.tagtype:
            if info.type:
                self.tagtype[tag] = info.type
            else:
                self.tagtype[tag] = 7
                if all(isinstance(v, IFDRational) for v in values):
                    self.tagtype[tag] = 5
                elif all(isinstance(v, int) for v in values):
                    if all(v < 2 ** 16 for v in values):
                        self.tagtype[tag] = 3
                    else:
                        self.tagtype[tag] = 4
                elif all(isinstance(v, float) for v in values):
                    self.tagtype[tag] = 12
                else:
                    if bytes is str:
                        # Never treat data as binary by default on Python 2.
                        self.tagtype[tag] = 2
                    else:
                        if all(isinstance(v, str) for v in values):
                            self.tagtype[tag] = 2

        if self.tagtype[tag] == 7 and bytes is not str:
            values = [value.encode("ascii", 'replace') if isinstance(value, str) else value]

        values = tuple(info.cvt_enum(value) for value in values)

        dest = self._tags_v1 if legacy_api else self._tags_v2

        if info.length == 1:
            if legacy_api and self.tagtype[tag] in [5, 10]:
                values = values,
            dest[tag], = values
        else:
            dest[tag] = values