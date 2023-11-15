    def __getitem__(self, key):
        val = self.file_content[key]
        if isinstance(val, h5py.Dataset):
            # these datasets are closed and inaccessible when the file is
            # closed, need to reopen
            return h5py.File(self.filename, 'r')[key].value
        return val