    def __setitem__(self, key, value):
        if not isinstance(key, str):

            def setitem_without_string_columns(df):
                df[key] = value
                return df

            return self._update_inplace(
                self._default_to_pandas(setitem_without_string_columns)._query_compiler
            )
        if key not in self.columns:
            self.insert(loc=len(self.columns), column=key, value=value)
        elif len(self.index) == 0:
            new_self = DataFrame({key: value}, columns=self.columns)
            self._update_inplace(new_self._query_compiler)
        else:
            self._update_inplace(self._query_compiler.setitem(key, value))