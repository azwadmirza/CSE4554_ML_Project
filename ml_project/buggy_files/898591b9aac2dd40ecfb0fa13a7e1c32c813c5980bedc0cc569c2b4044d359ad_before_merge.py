    def _iter_data(self):
        from pandas.core.frame import DataFrame
        if isinstance(self.data, (Series, np.ndarray)):
            yield com._stringify(self.label), np.asarray(self.data)
        elif isinstance(self.data, DataFrame):
            df = self.data

            if self.sort_columns:
                columns = com._try_sort(df.columns)
            else:
                columns = df.columns

            for col in columns:
                empty = df[col].count() == 0
                # is this right?
                values = df[col].values if not empty else np.zeros(len(df))

                col = com._stringify(col)
                yield col, values