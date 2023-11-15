    def get_dataset(self, key, info, out=None,
                    xslice=slice(None), yslice=slice(None)):

        if key.name not in self.channel_order_list:
            raise KeyError('Channel % s not available in the file' % key.name)
        elif key.name not in ['HRV']:
            ch_idn = self.channel_order_list.index(key.name)
            data = dec10216(
                self.memmap['visir']['line_data'][:, ch_idn, :])[::-1, ::-1]

            data = np.ma.masked_array(data, mask=(data == 0))
            res = Dataset(data, dtype=np.float32)
        else:
            data2 = dec10216(
                self.memmap["hrv"]["line_data"][:, 2, :])[::-1, ::-1]
            data1 = dec10216(
                self.memmap["hrv"]["line_data"][:, 1, :])[::-1, ::-1]
            data0 = dec10216(
                self.memmap["hrv"]["line_data"][:, 0, :])[::-1, ::-1]
            # Make empty array:
            shape = data0.shape[0] * 3, data0.shape[1]
            data = np.zeros(shape)
            idx = range(0, shape[0], 3)
            data[idx, :] = data2
            idx = range(1, shape[0], 3)
            data[idx, :] = data1
            idx = range(2, shape[0], 3)
            data[idx, :] = data0

            data = np.ma.masked_array(data, mask=(data == 0))
            res = Dataset(data, dtype=np.float32)

        if res is not None:
            out = res
        else:
            return None

        self.calibrate(out, key)
        out.info['units'] = info['units']
        out.info['wavelength'] = info['wavelength']
        out.info['standard_name'] = info['standard_name']
        out.info['platform_name'] = self.platform_name
        out.info['sensor'] = 'seviri'

        return out