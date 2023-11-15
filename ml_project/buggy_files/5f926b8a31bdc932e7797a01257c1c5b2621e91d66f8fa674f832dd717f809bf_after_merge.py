    def calibrate(self,
                  dataset_ids,
                  pre_launch_coeffs=False,
                  calib_coeffs=None):
        """Calibrate the data
        """
        tic = datetime.now()

        if calib_coeffs is None:
            calib_coeffs = {}

        chns = dict((dataset_id.name, dataset_id)
                    for dataset_id in dataset_ids)

        res = []
        # FIXME this should be done in _vis_calibrate
        units = {'reflectance': '%',
                 'brightness_temperature': 'K',
                 'counts': '',
                 'radiance': 'W*m-2*sr-1*cm ?'}

        if ("3a" in chns or "3b" in chns) and self._is3b is None:
            # Is it 3a or 3b:
            is3b = np.expand_dims(
                np.bitwise_and(
                    np.right_shift(self._data['scnlinbit'], 0), 1) == 1, 1)
            self._is3b = np.repeat(is3b,
                                   self._data['hrpt'][0].shape[0], axis=1)

        for idx, name in enumerate(['1', '2', '3a']):
            if name in chns:
                coeffs = calib_coeffs.get('ch' + name)
                # FIXME data should be masked before calibration
                ds = create_xarray(
                    _vis_calibrate(self._data,
                                   idx,
                                   chns[name].calibration,
                                   pre_launch_coeffs,
                                   coeffs,
                                   mask=(name == '3a' and self._is3b)).filled(np.nan))

                ds.attrs['units'] = units[chns[name].calibration]
                ds.attrs.update(chns[name]._asdict())
                res.append(ds)

        for idx, name in enumerate(['3b', '4', '5']):
            if name in chns:
                ds = create_xarray(
                    _ir_calibrate(self._header,
                                  self._data,
                                  idx,
                                  chns[name].calibration,
                                  mask=(name == '3b' and
                                        (np.logical_not(self._is3b)))).filled(np.nan))

                ds.attrs['units'] = units[chns[name].calibration]
                ds.attrs.update(chns[name]._asdict())
                res.append(ds)

        logger.debug("Calibration time %s", str(datetime.now() - tic))

        return res