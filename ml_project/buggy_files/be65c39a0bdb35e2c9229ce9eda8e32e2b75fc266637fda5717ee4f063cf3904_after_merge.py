    def get_dataset(self, dataset_id, ds_info):
        var_path = ds_info.get('file_key', '{}'.format(dataset_id.name))
        metadata = self.get_metadata(dataset_id, ds_info)
        valid_min, valid_max = self.get(var_path + '/attr/valid_range',
                                        self.get(var_path + '/attr/ValidRange', (None, None)))
        if valid_min is None or valid_max is None:
            raise KeyError("File variable '{}' has no valid range attribute".format(var_path))
        fill_name = var_path + '/attr/{}'.format(self._fill_name)
        if fill_name in self:
            fill_value = self[fill_name]
        else:
            fill_value = None

        data = self[var_path]
        scale_factor_path = var_path + '/attr/ScaleFactor'
        if scale_factor_path in self:
            scale_factor = self[scale_factor_path]
            scale_offset = self[var_path + '/attr/Offset']
        else:
            scale_factor = None
            scale_offset = None

        if valid_min is not None and valid_max is not None:
            # the original .cfg/INI based reader only checked valid_max
            data = data.where((data <= valid_max) & (data >= valid_min))
        if fill_value is not None:
            data = data.where(data != fill_value)

        factors = (scale_factor, scale_offset)
        factors = self.adjust_scaling_factors(factors, metadata['file_units'], ds_info.get("units"))
        if factors[0] != 1 or factors[1] != 0:
            data = data * factors[0] + factors[1]

        data.attrs.update(metadata)
        return data