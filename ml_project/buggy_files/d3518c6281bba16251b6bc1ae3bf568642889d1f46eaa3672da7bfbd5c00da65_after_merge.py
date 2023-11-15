    def _call_input_tensor(self, input_tensor, index, columns):
        if input_tensor.ndim not in {1, 2}:
            raise ValueError('Must pass 1-d or 2-d input')
        inputs = [input_tensor]

        if index is not None:
            if input_tensor.shape[0] != len(index):
                raise ValueError(
                    f'index {index} should have the same shape with tensor: {input_tensor.shape[0]}')
            index_value = self._process_index(index, inputs)
        elif isinstance(input_tensor, SERIES_TYPE):
            index_value = input_tensor.index_value
        else:
            stop = input_tensor.shape[0]
            stop = -1 if np.isnan(stop) else stop
            index_value = parse_index(pd.RangeIndex(start=0, stop=stop))

        if columns is not None:
            if not (input_tensor.ndim == 1 and len(columns) == 1 or
                    input_tensor.shape[1] == len(columns)):
                raise ValueError(
                    f'columns {columns} should have the same shape with tensor: {input_tensor.shape[1]}')
            if not isinstance(columns, pd.Index):
                if isinstance(columns, Base):
                    raise NotImplementedError('The columns value cannot be a tileable')
                columns = pd.Index(columns)
            columns_value = parse_index(columns, store_data=True)
        else:
            if input_tensor.ndim == 1:
                # convert to 1-d DataFrame
                columns_value = parse_index(pd.RangeIndex(start=0, stop=1), store_data=True)
            else:
                columns_value = parse_index(pd.RangeIndex(start=0, stop=input_tensor.shape[1]), store_data=True)

        if input_tensor.ndim == 1:
            shape = (input_tensor.shape[0], 1)
        else:
            shape = input_tensor.shape

        return self.new_dataframe(inputs, shape, dtypes=self.dtypes,
                                  index_value=index_value, columns_value=columns_value)