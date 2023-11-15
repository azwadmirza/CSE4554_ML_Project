    def calibrate(self,
                  dataset_id,
                  pre_launch_coeffs=False,
                  calib_coeffs=None):
        """Calibrate the data."""
        if calib_coeffs is None:
            calib_coeffs = {}

        units = {'reflectance': '%',
                 'brightness_temperature': 'K',
                 'counts': '',
                 'radiance': 'W*m-2*sr-1*cm ?'}

        if dataset_id['name'] in ("3a", "3b") and self._is3b is None:
            # Is it 3a or 3b:
            self._is3a = da.bitwise_and(da.from_array(self._data['scnlinbit'],
                                                      chunks=LINE_CHUNK), 3) == 0
            self._is3b = da.bitwise_and(da.from_array(self._data['scnlinbit'],
                                                      chunks=LINE_CHUNK), 3) == 1

        if dataset_id['name'] == '3a' and not np.any(self._is3a):
            raise ValueError("Empty dataset for channel 3A")
        if dataset_id['name'] == '3b' and not np.any(self._is3b):
            raise ValueError("Empty dataset for channel 3B")

        try:
            vis_idx = ['1', '2', '3a'].index(dataset_id['name'])
            ir_idx = None
        except ValueError:
            vis_idx = None
            ir_idx = ['3b', '4', '5'].index(dataset_id['name'])

        mask = True
        if vis_idx is not None:
            coeffs = calib_coeffs.get('ch' + dataset_id['name'])
            if dataset_id['name'] == '3a':
                mask = self._is3a[:, None]
            ds = create_xarray(
                _vis_calibrate(self._data,
                               vis_idx,
                               dataset_id['calibration'],
                               pre_launch_coeffs,
                               coeffs,
                               mask=mask))
        else:
            if dataset_id['name'] == '3b':
                mask = self._is3b[:, None]
            ds = create_xarray(
                _ir_calibrate(self._header,
                              self._data,
                              ir_idx,
                              dataset_id['calibration'],
                              mask=mask))

        ds.attrs['units'] = units[dataset_id['calibration']]
        ds.attrs.update(dataset_id._asdict())
        return ds