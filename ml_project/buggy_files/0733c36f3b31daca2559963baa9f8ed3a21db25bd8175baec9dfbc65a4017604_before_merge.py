    def to_ddf(self, columns=None):
        return dask_cudf.read_parquet(
            self.paths,
            columns=columns,
            index=False,
            gather_statistics=False,
            split_row_groups=self.row_groups_per_part,
            storage_options=self.storage_options,
        )