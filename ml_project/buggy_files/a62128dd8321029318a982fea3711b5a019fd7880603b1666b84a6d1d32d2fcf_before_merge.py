    def _updated_key(self, new_key):
        # TODO should suport VectorizedIndexer
        if isinstance(new_key, VectorizedIndexer):
            raise NotImplementedError(
                'Vectorized indexing for {} is not implemented. Load your '
                'data first with .load() or .compute().'.format(type(self)))
        new_key = iter(expanded_indexer(new_key, self.ndim))
        key = []
        for size, k in zip(self.array.shape, self.key):
            if isinstance(k, integer_types):
                key.append(k)
            else:
                key.append(_index_indexer_1d(k, next(new_key), size))
        return OuterIndexer(key)