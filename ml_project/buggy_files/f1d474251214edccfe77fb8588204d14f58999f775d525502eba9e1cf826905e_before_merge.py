    def __call__(self, input_tensor, index, name):
        inputs = [input_tensor]
        if index is not None:
            if not isinstance(index, pd.Index):
                if isinstance(index, INDEX_TYPE):
                    self._index = index
                    index_value = index.index_value
                    inputs.append(index)
                elif isinstance(index, (Base, Entity)):
                    self._index = index
                    index = astensor(index)
                    if index.ndim != 1:
                        raise ValueError(f'index should be 1-d, got {index.ndim}-d')
                    index_value = parse_index(pd.Index([], dtype=index.dtype), index, type(self).__name__)
                    inputs.append(index)
                else:
                    index = pd.Index(index)
                    index_value = parse_index(index, store_data=True)
            else:
                index_value = parse_index(index, store_data=True)
        else:
            index_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[0]))
        return self.new_series(inputs, shape=input_tensor.shape, dtype=self.dtype,
                               index_value=index_value, name=name)