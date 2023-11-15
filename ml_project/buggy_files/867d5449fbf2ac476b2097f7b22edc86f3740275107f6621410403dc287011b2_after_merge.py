    def spark_df(self) -> spark.DataFrame:
        """ Return as Spark DataFrame. """
        return self._sdf.select(self.scols)