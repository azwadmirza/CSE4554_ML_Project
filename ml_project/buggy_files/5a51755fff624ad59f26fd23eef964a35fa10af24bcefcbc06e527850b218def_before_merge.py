    def __getitem__(self, key):
        if isinstance(key, indexing.VectorizedIndexer):
            raise NotImplementedError(
             'Vectorized indexing for {} is not implemented. Load your '
             'data first with .load() or .compute().'.format(type(self)))
        key = indexing.to_tuple(key)
        with self.datastore.ensure_open(autoclose=True):
            array = self.get_array()
            if key == () and self.ndim == 0:
                return array.get_value()
            return array[key]