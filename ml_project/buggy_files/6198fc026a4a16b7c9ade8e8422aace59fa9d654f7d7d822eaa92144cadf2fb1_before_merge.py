    def getdict_setenv(self, name, default=None, sep="\n", replace=True):
        value = self.getstring(name, None, replace=replace, crossonly=True)
        definitions = self._getdict(value, default=default, sep=sep)
        self._setenv = SetenvDict(definitions, reader=self)
        return self._setenv