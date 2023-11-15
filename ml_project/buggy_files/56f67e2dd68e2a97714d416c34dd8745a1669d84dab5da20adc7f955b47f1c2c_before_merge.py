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
        df.index.name = self.index.name
        return df