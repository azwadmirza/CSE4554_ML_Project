    def spark_df(self) -> spark.DataFrame:
        """ Return as Spark DataFrame. """
        if self._scol is None:
            sdf = self._sdf
        else:
            sdf = self._sdf.select(self.index_columns + [self._scol])
        return sdf.select(['`{}`'.format(name) for name in self.columns])