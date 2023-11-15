    def data(self, index, role=Qt.DisplayRole):
        """Cell content"""
        if not index.isValid():
            return to_qvariant()
        if role == Qt.DisplayRole or role == Qt.EditRole:
            column = index.column()
            row = index.row()
            if column == 0:
                df_idx = self.df_index[row]
                if is_type_text_string(df_idx):
                    # Don't perform any conversion on strings
                    # because it leads to differences between
                    # the data present in the dataframe and
                    # what is shown by Spyder
                    return df_idx
                else:
                    return to_qvariant(to_text_string(df_idx))
            else:
                value = self.get_value(row, column-1)
                if isinstance(value, float):
                    try:
                        return to_qvariant(self._format % value)
                    except (ValueError, TypeError):
                        # may happen if format = '%d' and value = NaN;
                        # see issue 4139
                        return to_qvariant(DEFAULT_FORMAT % value)
                elif is_type_text_string(value):
                    # Don't perform any conversion on strings
                    # because it leads to differences between
                    # the data present in the dataframe and
                    # what is shown by Spyder
                    return value
                else:
                    return to_qvariant(to_text_string(value))
        elif role == Qt.BackgroundColorRole:
            return to_qvariant(self.get_bgcolor(index))
        elif role == Qt.FontRole:
            return to_qvariant(get_font(font_size_delta=DEFAULT_SMALL_DELTA))
        return to_qvariant()