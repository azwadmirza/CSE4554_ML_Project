    def _getitem_slice(self, key):
        if key.start is None and key.stop is None:
            return self.copy()
        return self.iloc[key]