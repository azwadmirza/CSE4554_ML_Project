    def __call__(self, obj):
        if isinstance(obj, DATAFRAME_TYPE):
            self._object_type = ObjectType.dataframe
            return self.new_dataframe([obj], shape=obj.shape, dtypes=obj.dtypes,
                                      index_value=obj.index_value,
                                      columns_value=obj.columns_value)
        else:
            assert isinstance(obj, SERIES_TYPE)
            self._object_type = ObjectType.series
            return self.new_series([obj], shape=obj.shape, dtype=obj.dtype,
                                   index_value=obj.index_value, name=obj.name)