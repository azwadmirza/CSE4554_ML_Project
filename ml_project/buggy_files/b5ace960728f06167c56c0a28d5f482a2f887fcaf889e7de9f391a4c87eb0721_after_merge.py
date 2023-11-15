    def get_ddf(self):
        if self.ddf is None:
            raise ValueError("No dask_cudf frame available.")
        elif isinstance(self.ddf, Dataset):
            # Right now we can't distinguish between input columns and generated columns
            # in the dataset, we don't limit the columm set right now in the to_ddf call
            # (https://github.com/NVIDIA/NVTabular/issues/409 )
            return self.ddf.to_ddf(shuffle=self._shuffle_parts)
        return self.ddf