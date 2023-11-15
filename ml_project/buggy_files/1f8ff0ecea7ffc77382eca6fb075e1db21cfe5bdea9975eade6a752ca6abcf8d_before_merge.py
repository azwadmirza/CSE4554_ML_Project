    def __call__(self, input_tensor, index, columns):
        if index is not None or columns is not None:
            if input_tensor.shape != (len(index), len(columns)):
                raise ValueError(
                    '({0},{1}) should have the same shape with tensor: {2}'.format(index, columns, input_tensor.shape))
        if input_tensor.ndim == 1:
            # convert to 1-d DataFrame
            index_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[0]))
            columns_value = parse_index(pd.RangeIndex(start=0, stop=1))
        elif input_tensor.ndim != 2:
            raise ValueError('Must pass 1-d or 2-d input')
        else:
            # convert to DataFrame
            index_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[0]))
            columns_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[1]))

        # overwrite index_value and columns_value if user has set them
        if index is not None:
            index_value = parse_index(index, store_data=True)
        if columns is not None:
            columns_value = parse_index(columns, store_data=True)

        return self.new_dataframe([input_tensor], input_tensor.shape, dtypes=self.dtypes,
                                  index_value=index_value,
                                  columns_value=columns_value)