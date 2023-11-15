    def __getitem__(self, keys):
        with open(self.path, 'rb') as pp_file:
            pp_file.seek(self.offset, os.SEEK_SET)
            data_bytes = pp_file.read(self.data_len)
            data = _data_bytes_to_shaped_array(data_bytes,
                                               self.lbpack,
                                               self.boundary_packing,
                                               self.shape, self.src_dtype,
                                               self.mdi, self.mask)
        data = data.__getitem__(keys)
        return np.asanyarray(data, dtype=self.dtype)