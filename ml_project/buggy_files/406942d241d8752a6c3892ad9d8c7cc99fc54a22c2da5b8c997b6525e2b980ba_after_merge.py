    def get_dataset(self, dataset_id, ds_info):
        """Load data array and metadata for specified dataset"""
        var_path = ds_info.get('file_key', '{}'.format(dataset_id.name))
        metadata = self.get_metadata(dataset_id, ds_info)
        valid_min, valid_max = self[var_path + '/attr/valid_range']
        fill_value = self.get(var_path + '/attr/_FillValue')

        d_tmp = self[var_path]
        if "index" in ds_info:
            d_tmp = d_tmp[int(ds_info["index"])]
        if "pressure_index" in ds_info:
            d_tmp = d_tmp[..., int(ds_info["pressure_index"])]
            # this is a pressure based field
            # include surface_pressure as metadata
            sp = self['Surface_Pressure']
            if 'surface_pressure' in ds_info:
                ds_info['surface_pressure'] = xr.concat((ds_info['surface_pressure'], sp))
            else:
                ds_info['surface_pressure'] = sp
            # include all the pressure levels
            ds_info.setdefault('pressure_levels', self['Pressure'][0])
        data = d_tmp

        if valid_min is not None and valid_max is not None:
            # the original .cfg/INI based reader only checked valid_max
            data = data.where((data <= valid_max))  # | (data >= valid_min))
        if fill_value is not None:
            data = data.where(data != fill_value)

        data.attrs.update(metadata)
        return data