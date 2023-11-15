    def astype(self, dtype) -> "Series":
        """
        Cast a Koalas object to a specified dtype ``dtype``.

        Parameters
        ----------
        dtype : data type
            Use a numpy.dtype or Python type to cast entire pandas object to
            the same type.

        Returns
        -------
        casted : same type as caller

        See Also
        --------
        to_datetime : Convert argument to datetime.

        Examples
        --------
        >>> ser = ks.Series([1, 2], dtype='int32')
        >>> ser
        0    1
        1    2
        dtype: int32

        >>> ser.astype('int64')
        0    1
        1    2
        dtype: int64
        """
        from databricks.koalas.typedef import as_spark_type

        spark_type = as_spark_type(dtype)
        if not spark_type:
            raise ValueError("Type {} not understood".format(dtype))
        if isinstance(spark_type, BooleanType):
            if isinstance(self.spark.data_type, StringType):
                scol = F.when(self.spark.column.isNull(), F.lit(False)).otherwise(
                    F.length(self.spark.column) > 0
                )
            elif isinstance(self.spark.data_type, (FloatType, DoubleType)):
                scol = F.when(
                    self.spark.column.isNull() | F.isnan(self.spark.column), F.lit(True)
                ).otherwise(self.spark.column.cast(spark_type))
            else:
                scol = F.when(self.spark.column.isNull(), F.lit(False)).otherwise(
                    self.spark.column.cast(spark_type)
                )
        elif isinstance(spark_type, StringType):
            scol = F.when(self.spark.column.isNull(), str(None)).otherwise(
                self.spark.column.cast(spark_type)
            )
        else:
            scol = self.spark.column.cast(spark_type)
        return self._with_new_scol(scol)