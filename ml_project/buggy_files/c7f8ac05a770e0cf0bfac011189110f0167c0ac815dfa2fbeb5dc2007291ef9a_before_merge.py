    def insert(self, loc, column, value, allow_duplicates=False):
        if isinstance(value, (DataFrame, pandas.DataFrame)):
            if len(value.columns) != 1:
                raise ValueError("Wrong number of items passed 2, placement implies 1")
            value = value.iloc[:, 0]

        if isinstance(value, Series):
            # TODO: Remove broadcast of Series
            value = value._to_pandas()

        if not self._query_compiler.lazy_execution and len(self.index) == 0:
            try:
                value = pandas.Series(value)
            except (TypeError, ValueError, IndexError):
                raise ValueError(
                    "Cannot insert into a DataFrame with no defined index "
                    "and a value that cannot be converted to a "
                    "Series"
                )
            new_index = value.index.copy()
            new_columns = self.columns.insert(loc, column)
            new_query_compiler = DataFrame(
                value, index=new_index, columns=new_columns
            )._query_compiler
        elif len(self.columns) == 0 and loc == 0:
            new_query_compiler = DataFrame(
                data=value, columns=[column], index=self.index
            )._query_compiler
        else:
            if (
                is_list_like(value)
                and not isinstance(value, pandas.Series)
                and len(value) != len(self.index)
            ):
                raise ValueError("Length of values does not match length of index")
            if not allow_duplicates and column in self.columns:
                raise ValueError("cannot insert {0}, already exists".format(column))
            if loc > len(self.columns):
                raise IndexError(
                    "index {0} is out of bounds for axis 0 with size {1}".format(
                        loc, len(self.columns)
                    )
                )
            if loc < 0:
                raise ValueError("unbounded slice")
            new_query_compiler = self._query_compiler.insert(loc, column, value)

        self._update_inplace(new_query_compiler=new_query_compiler)