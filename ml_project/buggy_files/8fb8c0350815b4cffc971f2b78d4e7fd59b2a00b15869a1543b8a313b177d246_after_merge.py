    def __getitem__(self, key):
        val = self.file_content[key]
        if isinstance(val, h5py.Dataset):
            # these datasets are closed and inaccessible when the file is closed, need to reopen
            dset = h5py.File(self.filename, 'r')[key]
            dset = da.from_array(dset, chunks=CHUNK_SIZE)
            if dset.ndim > 1:
                return xr.DataArray(dset, dims=['y', 'x'])
            else:
                return xr.DataArray(dset)

        return val