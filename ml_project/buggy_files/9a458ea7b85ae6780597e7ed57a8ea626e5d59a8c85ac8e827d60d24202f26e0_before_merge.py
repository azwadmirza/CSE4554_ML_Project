    def visibleText(self):
        if self._visibleText is None:
            self._visibleText = ''.join([c for c in self._layoutText if c not in codes.values()])
        return self._visibleText