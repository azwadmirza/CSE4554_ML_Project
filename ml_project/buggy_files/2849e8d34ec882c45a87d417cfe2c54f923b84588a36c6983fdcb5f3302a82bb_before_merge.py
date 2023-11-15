    def getdict(self, name, default=None, sep="\n", replace=True):
        value = self.getstring(name, None, replace=replace)
        return self._getdict(value, default=default, sep=sep)