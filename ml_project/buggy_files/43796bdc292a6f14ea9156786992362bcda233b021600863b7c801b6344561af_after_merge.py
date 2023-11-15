    def to_pandas(self):
        """Converts Modin DataFrame to Pandas DataFrame.

        Returns:
            Pandas DataFrame of the DataManager.
        """
        df = self.data.to_pandas(is_transposed=self._is_transposed)
        if df.empty:
            if len(self.columns) != 0:
                data = [
                    pandas.Series(dtype=self.dtypes[col_name], name=col_name)
                    for col_name in self.columns
                ]
                df = pandas.concat(data, axis=1)
            else:
                df = pandas.DataFrame(index=self.index)
        else:
            ErrorMessage.catch_bugs_and_request_email(
                len(df.index) != len(self.index) or len(df.columns) != len(self.columns)
            )
            df.index = self.index
            df.columns = self.columns
        return df