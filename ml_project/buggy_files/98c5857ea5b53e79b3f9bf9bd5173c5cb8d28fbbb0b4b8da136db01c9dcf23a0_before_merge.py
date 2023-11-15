    def __setitem__(self, key, value):
        if not isinstance(key, str):

            def setitem_without_string_columns(df):
                # Arrow makes memory-mapped objects immutable, so copy will allow them
                # to be mutable again.
                df = df.copy(True)
                df[key] = value
                return df

            return self._update_inplace(
                self._default_to_pandas(setitem_without_string_columns)._query_compiler
            )
        if is_list_like(value):
            if isinstance(value, (pandas.DataFrame, DataFrame)):
                if value.shape[1] != 1 and key not in self.columns:
                    raise ValueError(
                        "Wrong number of items passed %i, placement implies 1"
                        % value.shape[1]
                    )
                value = value[value.columns[0]].values
            elif isinstance(value, np.ndarray):
                if (
                    len(value.shape) > 1
                    and value.shape[1] != 1
                    and key not in self.columns
                ):
                    raise ValueError(
                        "Wrong number of items passed %i, placement implies 1"
                        % value.shape[1]
                    )
                assert (
                    len(value.shape) < 3
                ), "Shape of new values must be compatible with manager shape"
                value = value.T.reshape(-1)
                if len(self) > 0:
                    value = value[: len(self)]
            if not isinstance(value, Series):
                value = list(value)
        if key not in self.columns:
            if isinstance(value, Series):
                self._create_or_update_from_compiler(
                    self._query_compiler.concat(1, value._query_compiler), inplace=True
                )
                # Now that the data is appended, we need to update the column name for
                # that column to `key`, otherwise the name could be incorrect. Drop the
                # last column name from the list (the appended value's name and append
                # the new name.
                self.columns = self.columns[:-1].append(pandas.Index([key]))
            else:
                self.insert(loc=len(self.columns), column=key, value=value)
        elif len(self.index) == 0:
            new_self = DataFrame({key: value}, columns=self.columns)
            self._update_inplace(new_self._query_compiler)
        else:
            if isinstance(value, Series):
                value = value._query_compiler
            self._update_inplace(self._query_compiler.setitem(0, key, value))