    def _getitem_when_not_present(self, idx):
        return self._setitem_when_not_present(idx, None)