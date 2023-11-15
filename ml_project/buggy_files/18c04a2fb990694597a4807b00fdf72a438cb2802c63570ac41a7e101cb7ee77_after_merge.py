    def read_band(self, key, info):
        """Read the data"""
        # TODO slicing !
        tic = datetime.now()

        if self.mda['number_of_bits_per_pixel'] == 16:
            dtype = '>u2'
        elif self.mda['number_of_bits_per_pixel'] in [8, 10]:
            dtype = np.uint8
        shape = (int(np.ceil(self.mda['data_field_length'] / 8.)),)


        data = np.memmap(self.filename, mode='r',
                           offset=self.mda['total_header_length'],
                           dtype=dtype,
                           shape=shape)
        data = da.from_array(data, chunks=shape[0])
        if self.mda['number_of_bits_per_pixel'] == 10:
            data = dec10216(data)
        data = data.reshape((self.mda['number_of_lines'],
                             self.mda['number_of_columns'])).astype(np.float32)
        logger.debug("Reading time " + str(datetime.now() - tic))
        return data