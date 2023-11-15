    def __getitem__(self, aslice):
        ret = self._list[aslice]
        if ret:
            return type(self)(ret)

        return ret