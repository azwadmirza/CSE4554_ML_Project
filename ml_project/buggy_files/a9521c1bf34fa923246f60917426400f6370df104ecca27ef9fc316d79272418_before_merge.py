    def setitem(self, axis, key, value):
        """Set the column defined by `key` to the `value` provided.

        Args:
            key: The column name to set.
            value: The value to set the column to.

        Returns:
             A new QueryCompiler
        """

        def setitem_builder(df, internal_indices=[]):
            df = df.copy()
            if len(internal_indices) == 1:
                if axis == 0:
                    df[df.columns[internal_indices[0]]] = value
                else:
                    df.iloc[internal_indices[0]] = value
            else:
                if axis == 0:
                    df[df.columns[internal_indices]] = value
                else:
                    df.iloc[internal_indices] = value
            return df

        if isinstance(value, type(self)):
            value.columns = [key]
            if axis == 0:
                idx = self.columns.get_indexer_for([key])[0]
                if 0 < idx < len(self.columns) - 1:
                    first_mask = self._modin_frame.mask(
                        col_numeric_idx=list(range(idx))
                    )
                    second_mask = self._modin_frame.mask(
                        col_numeric_idx=list(range(idx + 1, len(self.columns)))
                    )
                    return self.__constructor__(
                        first_mask._concat(
                            1, [value._modin_frame, second_mask], "inner", False
                        )
                    )
                else:
                    mask = self.drop(columns=[key])._modin_frame
                    if idx == 0:
                        return self.__constructor__(
                            value._modin_frame._concat(1, [mask], "inner", False)
                        )
                    else:
                        return self.__constructor__(
                            mask._concat(1, [value._modin_frame], "inner", False)
                        )
            else:
                value = value.transpose()
                idx = self.index.get_indexer_for([key])[0]
                if 0 < idx < len(self.index) - 1:
                    first_mask = self._modin_frame.mask(
                        row_numeric_idx=list(range(idx))
                    )
                    second_mask = self._modin_frame.mask(
                        row_numeric_idx=list(range(idx + 1, len(self.index)))
                    )
                    return self.__constructor__(
                        first_mask._concat(
                            0, [value._modin_frame, second_mask], "inner", False
                        )
                    )
                else:
                    mask = self.drop(index=[key])._modin_frame
                    if idx == 0:
                        return self.__constructor__(
                            value._modin_frame._concat(0, [mask], "inner", False)
                        )
                    else:
                        return self.__constructor__(
                            mask._concat(0, [value._modin_frame], "inner", False)
                        )
        if is_list_like(value):
            new_modin_frame = self._modin_frame._apply_full_axis_select_indices(
                axis,
                setitem_builder,
                [key],
                new_index=self.index,
                new_columns=self.columns,
                keep_remaining=True,
            )
        else:
            new_modin_frame = self._modin_frame._apply_select_indices(
                axis,
                setitem_builder,
                [key],
                new_index=self.index,
                new_columns=self.columns,
                keep_remaining=True,
            )
        return self.__constructor__(new_modin_frame)