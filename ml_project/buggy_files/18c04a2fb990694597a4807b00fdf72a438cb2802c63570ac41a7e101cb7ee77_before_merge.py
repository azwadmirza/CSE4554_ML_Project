    def read_band(self, key, info,
                  out=None, xslice=slice(None), yslice=slice(None)):
        """Read the data"""
        # TODO slicing !
        tic = datetime.now()

        with open(self.filename, "rb") as fp_:
            fp_.seek(self.mda['total_header_length'])
            if self.mda['number_of_bits_per_pixel'] == 10:
                data = np.fromfile(fp_, dtype=np.uint8, count=int(np.ceil(
                    self.mda['data_field_length'] / 8.)))
                out.data[:] = dec10216(data).reshape((self.mda['number_of_lines'],
                                                      self.mda['number_of_columns']))[yslice, xslice] * 1.0
            elif self.mda['number_of_bits_per_pixel'] == 16:
                data = np.fromfile(fp_, dtype='>u2', count=int(np.ceil(
                    self.mda['data_field_length'] / 8.)))
                out.data[:] = data.reshape((self.mda['number_of_lines'],
                                            self.mda['number_of_columns']))[yslice, xslice] * 1.0
            elif self.mda['number_of_bits_per_pixel'] == 8:
                data = np.fromfile(fp_, dtype='>u1', count=int(np.ceil(
                    self.mda['data_field_length'] / 8.)))
                out.data[:] = data.reshape((self.mda['number_of_lines'],
                                            self.mda['number_of_columns']))[yslice, xslice] * 1.0
            out.mask[:] = out.data == 0
        logger.debug("Reading time " + str(datetime.now() - tic))