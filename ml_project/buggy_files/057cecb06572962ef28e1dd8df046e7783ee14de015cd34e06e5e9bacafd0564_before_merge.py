    def to_ddf(self, columns=None):
        return dask_cudf.read_csv(
            self.paths, names=self.names, chunksize=self.part_size, **self.csv_kwargs
        )[columns]