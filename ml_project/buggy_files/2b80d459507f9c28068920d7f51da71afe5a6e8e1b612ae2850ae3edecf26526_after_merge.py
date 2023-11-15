    def getitem(self, idx):
        ptr = self._gep(idx)
        data_item = self._builder.load(ptr)
        return self._datamodel.from_data(self._builder, data_item)