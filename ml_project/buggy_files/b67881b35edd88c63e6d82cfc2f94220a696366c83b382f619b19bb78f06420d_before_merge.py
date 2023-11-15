    def write(
        self,
        df: DataFrame,
        path,
        compression="snappy",
        index: Optional[bool] = None,
        partition_cols=None,
        **kwargs,
    ):
        self.validate_dataframe(df)
        path, _, _, _ = get_filepath_or_buffer(path, mode="wb")

        from_pandas_kwargs: Dict[str, Any] = {"schema": kwargs.pop("schema", None)}
        if index is not None:
            from_pandas_kwargs["preserve_index"] = index

        table = self.api.Table.from_pandas(df, **from_pandas_kwargs)
        if partition_cols is not None:
            self.api.parquet.write_to_dataset(
                table,
                path,
                compression=compression,
                partition_cols=partition_cols,
                **kwargs,
            )
        else:
            self.api.parquet.write_table(table, path, compression=compression, **kwargs)