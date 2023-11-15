    def get_dataset(self, dataset_id, ds_info, out=None, xslice=slice(None), yslice=slice(None)):
        var_path = ds_info.get('file_key', 'observation_data/{}'.format(dataset_id.name))
        dtype = ds_info.get('dtype', np.float32)
        if var_path + '/shape' not in self:
            # loading a scalar value
            shape = 1
        else:
            shape = self[var_path + '/shape']

        if isinstance(shape, tuple) and len(shape) == 2:
            # 2D array
            if xslice.start is not None:
                shape = (shape[0], xslice.stop - xslice.start)
            if yslice.start is not None:
                shape = (yslice.stop - yslice.start, shape[1])
        elif isinstance(shape, tuple) and len(shape) == 1 and yslice.start is not None:
            shape = ((yslice.stop - yslice.start) / yslice.step,)

        file_units = ds_info.get('file_units')
        if file_units is None:
            try:
                file_units = self[var_path + '/attr/units']
                # they were almost completely CF compliant...
                if file_units == "none":
                    file_units = "1"
            except KeyError:
                # no file units specified
                file_units = None

        if out is None:
            out = np.ma.empty(shape, dtype=dtype)
            out.mask = np.zeros(shape, dtype=np.bool)

        if dataset_id.calibration == 'radiance' and ds_info['units'] == 'W m-2 um-1 sr-1':
            rad_units_path = var_path + '/attr/radiance_units'
            if rad_units_path in self:
                # we are getting a reflectance band but we want the radiance values
                # special scaling parameters
                scale_factor = self[var_path + '/attr/radiance_scale_factor']
                scale_offset = self[var_path + '/attr/radiance_add_offset']
                if file_units is None:
                    file_units = self[var_path + '/attr/radiance_units']
                if file_units == 'Watts/meter^2/steradian/micrometer':
                    file_units = 'W m-2 um-1 sr-1'
            else:
                # we are getting a btemp band but we want the radiance values
                # these are stored directly in the primary variable
                scale_factor = self[var_path + '/attr/scale_factor']
                scale_offset = self[var_path + '/attr/add_offset']
            out.data[:] = self._load_and_slice(dtype, var_path, shape, xslice, yslice)
            valid_min = self[var_path + '/attr/valid_min']
            valid_max = self[var_path + '/attr/valid_max']
        elif ds_info.get('units') == '%':
            # normal reflectance
            out.data[:] = self._load_and_slice(dtype, var_path, shape, xslice, yslice)
            valid_min = self[var_path + '/attr/valid_min']
            valid_max = self[var_path + '/attr/valid_max']
            scale_factor = self[var_path + '/attr/scale_factor']
            scale_offset= self[var_path + '/attr/add_offset']
            # v1.1 and above of level 1 processing removed 'units' attribute
            # for all reflectance channels
            if file_units is None:
                file_units = "1"
        elif ds_info.get('units') == 'K':
            # normal brightness temperature
            # use a special LUT to get the actual values
            lut_var_path = ds_info.get('lut', var_path + '_brightness_temperature_lut')
            # we get the BT values from a look up table using the scaled radiance integers
            out.data[:] = np.require(self[lut_var_path][:][self[var_path][yslice, xslice].ravel()], dtype=dtype).reshape(shape)
            valid_min = self[lut_var_path + '/attr/valid_min']
            valid_max = self[lut_var_path + '/attr/valid_max']
            scale_factor = scale_offset = None
        elif shape == 1:
            out.data[:] = self[var_path]
            scale_factor = None
            scale_offset = None
            valid_min = None
            valid_max = None
        else:
            out.data[:] = self._load_and_slice(dtype, var_path, shape, xslice, yslice)
            valid_min = self[var_path + '/attr/valid_min']
            valid_max = self[var_path + '/attr/valid_max']
            try:
                scale_factor = self[var_path + '/attr/scale_factor']
                scale_offset = self[var_path + '/attr/add_offset']
            except KeyError:
                scale_factor = scale_offset = None

        if valid_min is not None and valid_max is not None:
            out.mask[:] |= (out.data < valid_min) | (out.data > valid_max)

        factors = (scale_factor, scale_offset)
        factors = self.adjust_scaling_factors(factors, file_units, ds_info.get("units"))
        if factors[0] != 1 or factors[1] != 0:
            out.data[:] *= factors[0]
            out.data[:] += factors[1]

        # Get extra metadata
        if '/dimension/number_of_scans' in self:
            rows_per_scan = int(shape[0] / self['/dimension/number_of_scans'])
            ds_info.setdefault('rows_per_scan', rows_per_scan)

        i = getattr(out, 'info', {})
        i.update(ds_info)
        i.update(dataset_id.to_dict())
        i.update({
            "units": ds_info.get("units", file_units),
            "platform": self.platform_name,
            "sensor": self.sensor_name,
            "start_orbit": self.start_orbit_number,
            "end_orbit": self.end_orbit_number,
        })
        ds_info.update(dataset_id.to_dict())
        cls = ds_info.pop("container", Dataset)
        return cls(out.data, mask=out.mask, copy=False, **i)