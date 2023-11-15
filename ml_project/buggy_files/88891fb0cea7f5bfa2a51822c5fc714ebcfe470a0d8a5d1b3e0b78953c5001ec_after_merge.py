    def __setitem__(self, key, value):
        if hashable(key) and key not in self.columns:
            if isinstance(value, Series) and len(self.columns) == 0:
                self._query_compiler = value._query_compiler.copy()
                # Now that the data is appended, we need to update the column name for
                # that column to `key`, otherwise the name could be incorrect. Drop the
                # last column name from the list (the appended value's name and append
                # the new name.
                self.columns = self.columns[:-1].append(pandas.Index([key]))
                return
            elif (
                isinstance(value, (pandas.DataFrame, DataFrame)) and value.shape[1] != 1
            ):
                raise ValueError(
                    "Wrong number of items passed %i, placement implies 1"
                    % value.shape[1]
                )
            elif isinstance(value, np.ndarray) and len(value.shape) > 1:
                if value.shape[1] == 1:
                    # Transform into columnar table and take first column
                    value = value.copy().T[0]
                else:
                    raise ValueError(
                        "Wrong number of items passed %i, placement implies 1"
                        % value.shape[1]
                    )

            # Do new column assignment after error checks and possible value modifications
            self.insert(loc=len(self.columns), column=key, value=value)
            return

        if not isinstance(key, str):

            if isinstance(key, DataFrame) or isinstance(key, np.ndarray):
                if isinstance(key, np.ndarray):
                    if key.shape != self.shape:
                        raise ValueError("Array must be same shape as DataFrame")
                    key = DataFrame(key, columns=self.columns)
                return self.mask(key, value, inplace=True)

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
                value = value[value.columns[0]].values
            elif isinstance(value, np.ndarray):
                assert (
                    len(value.shape) < 3
                ), "Shape of new values must be compatible with manager shape"
                value = value.T.reshape(-1)
                if len(self) > 0:
                    value = value[: len(self)]
            if not isinstance(value, Series):
                value = list(value)

        if not self._query_compiler.lazy_execution and len(self.index) == 0:
            new_self = DataFrame({key: value}, columns=self.columns)
            self._update_inplace(new_self._query_compiler)
        else:
            if isinstance(value, Series):
                value = value._query_compiler
            self._update_inplace(self._query_compiler.setitem(0, key, value))