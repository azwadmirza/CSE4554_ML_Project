    def get_dataset(self, dataset_id, ds_info, out=None):
        var_path = ds_info.get('file_key', '{}'.format(dataset_id.name))
        dtype = ds_info.get('dtype', np.float32)
        shape = self.get_shape(dataset_id, ds_info)
        file_units = ds_info.get('file_units')
        if file_units is None:
            file_units = self.get(var_path + '/attr/units', self.get(var_path + '/attr/Units'))
        if file_units is None:
            raise KeyError("File variable '{}' has no units attribute".format(var_path))
        elif file_units == 'deg':
            file_units = 'degrees'
        elif file_units == 'Unitless':
            file_units = '1'

        if out is None:
            out = np.ma.empty(shape, dtype=dtype)
            out.mask = np.zeros(shape, dtype=np.bool)

        valid_min, valid_max = self.get(var_path + '/attr/valid_range',
                                        self.get(var_path + '/attr/ValidRange', (None, None)))
        if valid_min is None or valid_max is None:
            raise KeyError("File variable '{}' has no valid range attribute".format(var_path))
        fill_name = var_path + '/attr/{}'.format(self._fill_name)
        if fill_name in self:
            fill_value = self[fill_name]
        else:
            fill_value = None

        out.data[:] = np.require(self[var_path][:], dtype=dtype)
        scale_factor_path = var_path + '/attr/ScaleFactor'
        if scale_factor_path in self:
            scale_factor = self[scale_factor_path]
            scale_offset = self[var_path + '/attr/Offset']
        else:
            scale_factor = None
            scale_offset = None

        if valid_min is not None and valid_max is not None:
            # the original .cfg/INI based reader only checked valid_max
            out.mask[:] |= (out.data > valid_max) | (out.data < valid_min)
        if fill_value is not None:
            out.mask[:] |= out.data == fill_value

        factors = (scale_factor, scale_offset)
        factors = self.adjust_scaling_factors(factors, file_units, ds_info.get("units"))
        if factors[0] != 1 or factors[1] != 0:
            out.data[:] *= factors[0]
            out.data[:] += factors[1]

        i = getattr(out, 'info', {})
        i.update(ds_info)
        i.update({
            "units": ds_info.get("units", file_units),
            "platform": self.platform_name,
            "sensor": self.sensor_name,
            "start_orbit": self.start_orbit_number,
            "end_orbit": self.end_orbit_number,
        })
        i.update(dataset_id.to_dict())
        if 'standard_name' not in ds_info:
            i['standard_name'] = self.get(var_path + '/attr/Title', dataset_id.name)
        cls = ds_info.pop("container", Dataset)
        return cls(out.data, mask=out.mask, copy=False, **i)