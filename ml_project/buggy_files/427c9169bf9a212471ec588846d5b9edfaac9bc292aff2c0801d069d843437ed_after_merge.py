    def __getitem__(self, key):
        val = self.file_content[key]
        if isinstance(val, netCDF4.Variable):
            # these datasets are closed and inaccessible when the file is
            # closed, need to reopen
            # TODO: Handle HDF4 versus NetCDF3 versus NetCDF4
            parts = key.rsplit('/', 1)
            if len(parts) == 2:
                group, key = parts
            else:
                group = None
            val = xr.open_dataset(self.filename, group=group, chunks=CHUNK_SIZE,
                                  mask_and_scale=self.auto_maskandscale)[key]
        return val