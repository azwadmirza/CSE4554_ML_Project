    def get_dataset(self, dataset_id, ds_info, out=None):
        """Load data array and metadata for specified dataset"""
        var_path = ds_info.get('file_key', '{}'.format(dataset_id.name))
        dtype = ds_info.get('dtype', np.float32)
        if var_path + '/shape' not in self:
            # loading a scalar value
            shape = 1
        else:
            shape = self.get_shape(dataset_id, ds_info)
        file_units = ds_info.get('file_units',
                                 self.get(var_path + '/attr/units'))

        if out is None:
            out = np.ma.empty(shape, dtype=dtype)
            out.mask = np.zeros(shape, dtype=np.bool)
            out.info = {}

        valid_min, valid_max = self[var_path + '/attr/valid_range']
        fill_value = self.get(var_path + '/attr/_FillValue')

        d_tmp = np.require(self[var_path][:], dtype=dtype)
        if "index" in ds_info:
            d_tmp = d_tmp[int(ds_info["index"])]
        if "pressure_index" in ds_info:
            d_tmp = d_tmp[..., int(ds_info["pressure_index"])]
            # this is a pressure based field
            # include surface_pressure as metadata
            sp = self['Surface_Pressure'][:]
            if 'surface_pressure' in ds_info:
                ds_info['surface_pressure'] = np.concatenate((ds_info['surface_pressure'], sp))
            else:
                ds_info['surface_pressure'] = sp
            # include all the pressure levels
            ds_info.setdefault('pressure_levels', self['Pressure'][0])
        out.data[:] = d_tmp
        del d_tmp

        if valid_min is not None and valid_max is not None:
            # the original .cfg/INI based reader only checked valid_max
            out.mask[:] |= (out.data > valid_max)  # | (out < valid_min)
        if fill_value is not None:
            out.mask[:] |= out.data == fill_value

        cls = ds_info.pop("container", Dataset)
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
        if 'standard_name' not in i:
            sname_path = var_path + '/attr/standard_name'
            i['standard_name'] = self.get(sname_path)
        if 'quality_flag' in i:
            i['quality_flag'] = np.concatenate((i['quality_flag'], self['Quality_Flag'][:]))
        else:
            i['quality_flag'] = self['Quality_Flag'][:]
        return cls(out.data, mask=out.mask, copy=False, **i)