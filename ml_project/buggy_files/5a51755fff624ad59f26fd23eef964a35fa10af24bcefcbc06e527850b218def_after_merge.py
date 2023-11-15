    def __getitem__(self, key):
        if isinstance(key, (indexing.VectorizedIndexer,
                            indexing.OuterIndexer)):
            raise NotImplementedError(
                'Nio backend does not support vectorized / outer indexing. '
                'Load your data first with .load() or .compute(). '
                'Given {}'.format(key))
        key = indexing.to_tuple(key)
        with self.datastore.ensure_open(autoclose=True):
            array = self.get_array()
            if key == () and self.ndim == 0:
                return array.get_value()
            return array[key]