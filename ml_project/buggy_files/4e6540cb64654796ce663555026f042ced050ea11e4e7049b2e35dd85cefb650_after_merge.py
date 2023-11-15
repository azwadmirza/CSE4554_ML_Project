    def __call__(self, df):
        if isinstance(self.indexes[0], TENSOR_TYPE) or isinstance(self.indexes[1], TENSOR_TYPE):
            raise NotImplementedError('The index value cannot be unexecuted mars tensor')
        return self.new_dataframe([df], shape=df.shape, dtypes=df.dtypes,
                                  index_value=df.index_value, columns_value=df.columns_value)