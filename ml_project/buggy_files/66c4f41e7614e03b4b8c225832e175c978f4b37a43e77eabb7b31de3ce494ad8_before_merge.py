    def _shallow_copy(self, values=None, **kwargs):
        """ create a new Index, don't copy the data, use the same object attributes
            with passed in attributes taking precedence """
        if values is None:
            return RangeIndex(name=self.name, fastpath=True,
                              **dict(self._get_data_as_items()))
        else:
            kwargs.setdefault('name', self.name)
            return self._int64index._shallow_copy(values, **kwargs)