    def get_dataset(self, key, info,
                    xslice=slice(None), yslice=slice(None)):

        if key.name not in self.channel_order_list:
            raise KeyError('Channel % s not available in the file' % key.name)
        elif key.name not in ['HRV']:
            ch_idn = self.channel_order_list.index(key.name)
            data = dec10216(
                self.memmap['visir']['line_data'][:, ch_idn, :])[::-1, ::-1]
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

        res = xr.DataArray(data, dims=['y', 'x']).where(data != 0).astype(np.float32)

        if res is not None:
            out = res
        else:
            return None

        self.calibrate(out, key)
        out.attrs['units'] = info['units']
        out.attrs['wavelength'] = info['wavelength']
        out.attrs['standard_name'] = info['standard_name']
        out.attrs['platform_name'] = self.platform_name
        out.attrs['sensor'] = 'seviri'

        return out