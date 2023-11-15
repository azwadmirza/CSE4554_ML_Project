    def get_shape(self, ds_id, ds_info):
        """Return data array shape for item specified.
        """
        var_path = ds_info.get('file_key', '{}'.format(ds_id.name))
        if var_path + '/shape' not in self:
            # loading a scalar value
            shape = 1
        else:
            shape = self[var_path + "/shape"]
            if "index" in ds_info:
                shape = shape[1:]
            if "pressure_index" in ds_info:
                shape = shape[:-1]
        return shape