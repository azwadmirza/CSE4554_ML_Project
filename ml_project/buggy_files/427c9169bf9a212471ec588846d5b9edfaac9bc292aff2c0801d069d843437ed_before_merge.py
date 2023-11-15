    def __getitem__(self, key):
        val = self.file_content[key]
        if isinstance(val, netCDF4.Variable):
            # these datasets are closed and inaccessible when the file is
            # closed, need to reopen
            v = netCDF4.Dataset(self.filename, 'r')
            val = v[key]
            val.set_auto_maskandscale(self.auto_maskandscale)
        return val