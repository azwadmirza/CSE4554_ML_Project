    def _column_X(self, idx, attrname):
        if self._is_fk:
            try:
                fk = self.const.elements[idx]
            except IndexError:
                return ""
            else:
                return getattr(fk.parent, attrname)
        else:
            cols = list(self.const.columns)
            try:
                col = cols[idx]
            except IndexError:
                return ""
            else:
                return getattr(col, attrname)