    def __call__(self, df):
        return self.new_dataframe([df], df.shape, dtypes=df.dtypes,
                                  columns_value=df.columns_value, index_value=df.index_value)