    def __call__(self, input_tensor, index, columns):
        if input_tensor.ndim != 1 and input_tensor.ndim != 2:
            raise ValueError('Must pass 1-d or 2-d input')

        if index is not None:
            if input_tensor.shape[0] != len(index):
                raise ValueError(
                    'index {0} should have the same shape with tensor: {1}'.format(index, input_tensor.shape[0]))
            if not isinstance(index, pd.Index):
                if isinstance(index, Base):
                    raise NotImplementedError('The index value cannot be a tileable')
                index = pd.Index(index)
            index_value = parse_index(index, store_data=True)
        else:
            index_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[0]))

        if columns is not None:
            if input_tensor.shape[1] != len(columns):
                raise ValueError(
                    'columns {0} should have the same shape with tensor: {1}'.format(columns, input_tensor.shape[1]))
            if not isinstance(columns, pd.Index):
                if isinstance(index, Base):
                    raise NotImplementedError('The index value cannot be a tileable')
                columns = pd.Index(columns)
            columns_value = parse_index(columns, store_data=True)
        else:
            if input_tensor.ndim == 1:
                # convert to 1-d DataFrame
                columns_value = parse_index(pd.RangeIndex(start=0, stop=1), store_data=True)
            else:
                columns_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[1]), store_data=True)

        return self.new_dataframe([input_tensor], input_tensor.shape, dtypes=self.dtypes,
                                  index_value=index_value,
                                  columns_value=columns_value)