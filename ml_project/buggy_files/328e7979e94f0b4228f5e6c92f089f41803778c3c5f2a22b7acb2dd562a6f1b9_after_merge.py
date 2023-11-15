    def __call__(self):
        num_class = self._model.attr('num_class')
        if num_class is not None:
            num_class = int(num_class)
        if num_class is not None:
            shape = (self._data.shape[0], num_class)
        else:
            shape = (self._data.shape[0],)
        inputs = [self._data]
        if self.output_types[0] == OutputType.tensor:
            # tensor
            return self.new_tileable(inputs, shape=shape, dtype=np.dtype(np.float32),
                                     order=TensorOrder.C_ORDER)
        elif self.output_types[0] == OutputType.dataframe:
            # dataframe
            dtypes = pd.DataFrame(np.random.rand(0, num_class), dtype=np.float32).dtypes
            return self.new_tileable(inputs, shape=shape, dtypes=dtypes,
                                     columns_value=parse_index(dtypes.index),
                                     index_value=self._data.index_value)
        else:
            # series
            return self.new_tileable(inputs, shape=shape, index_value=self._data.index_value,
                                     name='predictions', dtype=np.dtype(np.float32))