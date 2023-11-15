    def get_dataset(self, key, info, out=None, xslice=slice(None), yslice=slice(None)):
        to_return = out is None
        if out is None:
            nlines = int(self.mda['number_of_lines'])
            ncols = int(self.mda['number_of_columns'])
            out = Dataset(np.ma.empty((nlines, ncols), dtype=np.float32))

        self.read_band(key, info, out, xslice, yslice)

        if to_return:
            from satpy.yaml_reader import Shuttle
            return Shuttle(out.data, out.mask, out.info)