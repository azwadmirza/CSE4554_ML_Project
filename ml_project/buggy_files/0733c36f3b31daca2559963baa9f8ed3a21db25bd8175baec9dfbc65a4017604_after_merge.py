    def to_ddf(self, columns=None):
        return dask_cudf.read_parquet(
            self.paths,
            columns=columns,
            # can't omit reading the index in if we aren't being passed columns
            index=None if columns is None else False,
            gather_statistics=False,
            split_row_groups=self.row_groups_per_part,
            storage_options=self.storage_options,
        )