    def _call_input_1d_tileables(self, input_1d_tileables, index, columns):
        tileables = []
        shape = None
        for tileable in input_1d_tileables.values():
            tileable_shape = astensor(tileable).shape
            if len(tileable_shape) > 0:
                if shape is None:
                    shape = tileable_shape
                elif shape != tileable_shape:
                    raise ValueError('input 1-d tensors should have same shape')

            if isinstance(tileable, (Base, Entity)):
                tileables.append(tileable)

        if index is not None:
            if tileables[0].shape[0] != len(index):
                raise ValueError(
                    f'index {index} should have the same shape with tensor: {input_1d_tileables[0].shape[0]}')
            index_value = self._process_index(index, tileables)
        else:
            index_value = parse_index(pd.RangeIndex(0, tileables[0].shape[0]))

        if columns is not None:
            if len(input_1d_tileables) != len(columns):
                raise ValueError(
                    f'columns {columns} should have size {len(input_1d_tileables)}')
            if not isinstance(columns, pd.Index):
                if isinstance(columns, Base):
                    raise NotImplementedError('The columns value cannot be a tileable')
                columns = pd.Index(columns)
            columns_value = parse_index(columns, store_data=True)
        else:
            columns_value = parse_index(pd.RangeIndex(0, len(input_1d_tileables)), store_data=True)

        shape = (shape[0], len(input_1d_tileables))
        return self.new_dataframe(tileables, shape, dtypes=self.dtypes,
                                  index_value=index_value, columns_value=columns_value)