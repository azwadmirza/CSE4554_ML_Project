    def get_dataset(self, ds_id, ds_info):
        """Get output data and metadata of specified dataset"""
        var_path = ds_info['file_key']
        fill_value = ds_info.get('fill_value', 65535)
        metadata = self.get_metadata(ds_id, ds_info)

        data = self[var_path]
        if ((ds_info.get('standard_name') == "longitude" or
             ds_info.get('standard_name') == "latitude") and
                ds_id.resolution == 10000):
            # FIXME: Lower frequency channels need CoRegistration parameters applied
            data = data[:, ::2] * self[var_path + "/attr/SCALE FACTOR"]
        else:
            data = data * self[var_path + "/attr/SCALE FACTOR"]
        data = data.where(data != fill_value)
        data.attrs.update(metadata)
        return data