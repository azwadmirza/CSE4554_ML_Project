    def __getitem__(self, index):
        """Get a block by its index or name (if the name is non-unique then
        returns the first occurence)"""
        if isinstance(index, str):
            index = self.get_index_by_name(index)
        data = self.GetBlock(index)
        if data is None:
            return data
        if data is not None and not is_vtki_obj(data):
            data = wrap(data)
        return data