    def get_ddf(self):
        if self.ddf is None:
            raise ValueError("No dask_cudf frame available.")
        elif isinstance(self.ddf, Dataset):
            columns = self.columns_ctx["all"]["base"]
            return self.ddf.to_ddf(columns=columns, shuffle=self._shuffle_parts)
        return self.ddf