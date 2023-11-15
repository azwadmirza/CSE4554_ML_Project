    def getitem(self, idx):
        ptr = self._gep(idx)
        return self._builder.load(ptr)