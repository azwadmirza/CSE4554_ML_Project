    def __getitem__(self, key):
        if len(self) == 0:
            return self._default_to_pandas("__getitem__", key)
        # see if we can slice the rows
        # This lets us reuse code in Pandas to error check
        indexer = convert_to_index_sliceable(
            getattr(pandas, type(self).__name__)(index=self.index), key
        )
        if indexer is not None:
            return self._getitem_slice(indexer)
        else:
            return self._getitem(key)