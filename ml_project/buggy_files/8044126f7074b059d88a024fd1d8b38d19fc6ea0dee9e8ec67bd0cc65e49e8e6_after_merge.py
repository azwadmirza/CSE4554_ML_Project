    def create_dataset(self, name, shape=None, dtype=None, data=None, **kwds):
        """ Create a new HDF5 dataset

        name
            Name of the dataset (absolute or relative).  Provide None to make
            an anonymous dataset.
        shape
            Dataset shape.  Use "()" for scalar datasets.  Required if "data"
            isn't provided.
        dtype
            Numpy dtype or string.  If omitted, dtype('f') will be used.
            Required if "data" isn't provided; otherwise, overrides data
            array's dtype.
        data
            Provide data to initialize the dataset.  If used, you can omit
            shape and dtype arguments.

        Keyword-only arguments:

        chunks
            (Tuple or int) Chunk shape, or True to enable auto-chunking. Integers can
            be used for 1D shape.

        maxshape
            (Tuple or int) Make the dataset resizable up to this shape. Use None for
            axes you want to be unlimited. Integers can be used for 1D shape.
        compression
            (String or int) Compression strategy.  Legal values are 'gzip',
            'szip', 'lzf'.  If an integer in range(10), this indicates gzip
            compression level. Otherwise, an integer indicates the number of a
            dynamically loaded compression filter.
        compression_opts
            Compression settings.  This is an integer for gzip, 2-tuple for
            szip, etc. If specifying a dynamically loaded compression filter
            number, this must be a tuple of values.
        scaleoffset
            (Integer) Enable scale/offset filter for (usually) lossy
            compression of integer or floating-point data. For integer
            data, the value of scaleoffset is the number of bits to
            retain (pass 0 to let HDF5 determine the minimum number of
            bits necessary for lossless compression). For floating point
            data, scaleoffset is the number of digits after the decimal
            place to retain; stored values thus have absolute error
            less than 0.5*10**(-scaleoffset).
        shuffle
            (T/F) Enable shuffle filter.
        fletcher32
            (T/F) Enable fletcher32 error detection. Not permitted in
            conjunction with the scale/offset filter.
        fillvalue
            (Scalar) Use this value for uninitialized parts of the dataset.
        track_times
            (T/F) Enable dataset creation timestamps.
        track_order
            (T/F) Track attribute creation order if True. If omitted use
            global default h5.get_config().track_order.
        external
            (Iterable of tuples) Sets the external storage property, thus
            designating that the dataset will be stored in one or more
            non-HDF5 files external to the HDF5 file.  Adds each tuple
            of (name, offset, size) to the dataset's list of external files.
            Each name must be a str, bytes, or os.PathLike; each offset and
            size, an integer.  If only a name is given instead of an iterable
            of tuples, it is equivalent to [(name, 0, h5py.h5f.UNLIMITED)].
        allow_unknown_filter
            (T/F) Do not check that the requested filter is available for use.
            This should only be used with ``write_direct_chunk``, where the caller
            compresses the data before handing it to h5py.
        """
        if 'track_order' not in kwds:
            kwds['track_order'] = h5.get_config().track_order

        with phil:
            group = self
            if name:
                name = self._e(name)
                if b'/' in name.lstrip(b'/'):
                    parent_path, name = name.rsplit(b'/', 1)
                    group = self.require_group(parent_path)

            dsid = dataset.make_new_dset(group, shape, dtype, data, name, **kwds)
            dset = dataset.Dataset(dsid)
            return dset