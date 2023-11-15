    def inititem(self, idx, val):
        ptr = self._gep(idx)
        self._builder.store(val, ptr)