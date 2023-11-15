    def __call__(self, df):
        # Note [Fancy Index of Numpy and Pandas]
        #
        # The numpy and pandas.iloc have different semantic when processing fancy index:
        #
        # >>> np.ones((3,3))[[1,2],[1,2]]
        # array([1., 1.])
        #
        # >>> pd.DataFrame(np.ones((3,3))).iloc[[1,2],[1,2]]
        #    1    2
        # 1  1.0  1.0
        # 2  1.0  1.0
        #
        # Thus, we processing the index along two axis of DataFrame seperately.

        if isinstance(self.indexes[0], TENSOR_TYPE) or isinstance(self.indexes[1], TENSOR_TYPE):
            raise NotImplementedError('The index value cannot be unexecuted mars tensor')

        shape0 = tuple(calc_shape((df.shape[0],), (self.indexes[0],)))
        shape1 = tuple(calc_shape((df.shape[1],), (self.indexes[1],)))

        # NB: pandas only compresses the result to series when index on one of axis is integral
        if isinstance(self.indexes[1], Integral):
            shape = shape0
            dtype = df.dtypes.iloc[self.indexes[1]]
            index_value = indexing_index_value(df.index_value, self.indexes[0])
            self._object_type = ObjectType.series
            return self.new_series([df], shape=shape, dtype=dtype, index_value=index_value)
        elif isinstance(self.indexes[0], Integral):
            shape = shape1
            dtype = find_common_type(df.dtypes.iloc[self.indexes[1]].values)
            index_value = indexing_index_value(df.columns_value, self.indexes[1])
            self._object_type = ObjectType.series
            return self.new_series([df], shape=shape, dtype=dtype, index_value=index_value)
        else:
            return self.new_dataframe([df], shape=shape0 + shape1, dtypes=df.dtypes.iloc[self.indexes[1]],
                                      index_value=indexing_index_value(df.index_value, self.indexes[0]),
                                      columns_value=indexing_index_value(df.columns_value, self.indexes[1], store_data=True))