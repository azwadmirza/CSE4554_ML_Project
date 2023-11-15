    def setitem(self, idx, val):
        ptr = self._gep(idx)
        data_item = self._datamodel.as_data(self._builder, val)
        self._builder.store(data_item, ptr)