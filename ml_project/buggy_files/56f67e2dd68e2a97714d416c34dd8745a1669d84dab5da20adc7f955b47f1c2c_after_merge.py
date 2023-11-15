    def to_pandas(self):
        """Converts Modin DataFrame to Pandas DataFrame.

        Returns:
            Pandas DataFrame.
        """
        df = self._frame_mgr_cls.to_pandas(self._partitions)
        if df.empty:
            if len(self.columns) != 0:
                df = pandas.DataFrame(columns=self.columns)
            else:
                df = pandas.DataFrame(columns=self.columns, index=self.index)
        else:
            ErrorMessage.catch_bugs_and_request_email(
                not df.index.equals(self.index) or not df.columns.equals(self.columns),
                "Internal and external indices do not match.",
            )
            df.index = self.index
            df.columns = self.columns
        return df