    def parse_hypermap(self, index=0, downsample=1, cutoff_at_kV=None,
                       lazy=False):
        """Unpack the Delphi/Bruker binary spectral map and return
        numpy array in memory efficient way.

        Pure python/numpy implimentation -- slow, or
        cython/memoryview/numpy implimentation if compilied and present
        (fast) is used.

        Arguments:
        index -- the index of hypermap in bcf if there is more than one
            hyper map in file.
        downsample -- downsampling factor (integer). Diferently than
            block_reduce from skimage.measure, the parser populates
            reduced array by suming results of pixels, thus having lower
            memory requiriments. (default 1)
        cutoff_at_kV -- value in keV to truncate the array at. Helps reducing
          size of array. (default None)
        lazy -- return dask.array (True) or numpy.array (False) (default False)

        Returns:
        numpy or dask array of bruker hypermap, with (y,x,E) shape.
        """

        if type(cutoff_at_kV) in (int, float):
            eds = self.header.get_spectra_metadata()
            cutoff_chan = eds.energy_to_channel(cutoff_at_kV)
        else:
            cutoff_chan = None

        if fast_unbcf:
            fh = dd(self.get_file)('EDSDatabase/SpectrumData' + str(index))  # noqa
            value = dd(unbcf_fast.parse_to_numpy)(fh,                        # noqa
                                                  downsample=downsample,
                                                  cutoff=cutoff_chan,
                                                  description=False)
            if lazy:
                shape, dtype = unbcf_fast.parse_to_numpy(fh.compute(),
                                                         downsample=downsample,
                                                         cutoff=cutoff_chan,
                                                         description=True)
                res = da.from_delayed(value, shape=shape, dtype=dtype)
            else:
                res = value.compute()
            return res
        else:
            value = dd(self.py_parse_hypermap)(index=0,
                                               downsample=downsample,
                                               cutoff_at_channel=cutoff_chan,
                                               description=False)
            if lazy:
                shape, dtype = self.py_parse_hypermap(
                    index=0, downsample=downsample,
                    cutoff_at_channel=cutoff_chan, description=True)
                res = da.from_delayed(value, shape=shape, dtype=dtype)
            else:
                res = value.compute()
            return res