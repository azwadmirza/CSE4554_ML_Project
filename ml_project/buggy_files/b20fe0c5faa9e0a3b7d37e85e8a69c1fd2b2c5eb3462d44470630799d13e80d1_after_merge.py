    def get_dataset(self, dataset_id, ds_info, xslice=slice(None), yslice=slice(None)):
        var_path = ds_info.get('file_key', 'observation_data/{}'.format(dataset_id.name))
        metadata = self.get_metadata(dataset_id, ds_info)
        shape = metadata['shape']
        if isinstance(shape, tuple) and len(shape) == 2:
            # 2D array
            if xslice.start is not None:
                shape = (shape[0], xslice.stop - xslice.start)
            if yslice.start is not None:
                shape = (yslice.stop - yslice.start, shape[1])
        elif isinstance(shape, tuple) and len(shape) == 1 and yslice.start is not None:
            shape = ((yslice.stop - yslice.start) / yslice.step,)
        metadata['shape'] = shape

        valid_min, valid_max, scale_factor, scale_offset = self._get_dataset_valid_range(dataset_id, ds_info, var_path)
        if dataset_id.calibration == 'radiance' and ds_info['units'] == 'W m-2 um-1 sr-1':
            data = self._load_and_slice(var_path, shape, xslice, yslice)
        elif ds_info.get('units') == '%':
            data = self._load_and_slice(var_path, shape, xslice, yslice)
        elif ds_info.get('units') == 'K':
            # normal brightness temperature
            # use a special LUT to get the actual values
            lut_var_path = ds_info.get('lut', var_path + '_brightness_temperature_lut')
            # we get the BT values from a look up table using the scaled radiance integers
            # .flatten() currently not supported, workaround: https://github.com/pydata/xarray/issues/1029
            data = self[var_path][yslice, xslice]
            data = data.stack(name=data.dims).astype(np.int)
            coords = data.coords
            data = self[lut_var_path][data]
            if 'dim_0' in data:
                # seems like older versions of xarray take the dims from
                # 'lut_var_path'. newer versions take 'data' dims
                data = data.rename({'dim_0': 'name'})
            data = data.assign_coords(**coords).unstack('name')
        elif shape == 1:
            data = self[var_path]
        else:
            data = self._load_and_slice(var_path, shape, xslice, yslice)

        if valid_min is not None and valid_max is not None:
            data = data.where((data >= valid_min) & (data <= valid_max))

        factors = (scale_factor, scale_offset)
        factors = self.adjust_scaling_factors(factors, metadata['file_units'], ds_info.get("units"))
        if factors[0] != 1 or factors[1] != 0:
            data = data * factors[0] + factors[1]

        data.attrs.update(metadata)
        return data