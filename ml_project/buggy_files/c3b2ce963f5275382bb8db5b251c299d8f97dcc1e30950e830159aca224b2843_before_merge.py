    def _column_X(self, idx):
        if self._is_fk:
            fk = self.const.elements[idx]
            return fk.parent
        else:
            return list(self.const.columns)[idx]