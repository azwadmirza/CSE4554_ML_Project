    def get_dataset(self, dataset_id, ds_info, xslice=slice(None), yslice=slice(None)):
        var_name = ds_info.get('file_key', dataset_id.name)
        # FUTURE: Metadata retrieval may be separate
        info = self.get_metadata(dataset_id, ds_info)
        data = self[var_name][yslice, xslice]
        fill = self[var_name + '/attr/_FillValue']
        factor = self.get(var_name + '/attr/scale_factor')
        offset = self.get(var_name + '/attr/add_offset')
        valid_range = self.get(var_name + '/attr/valid_range')

        data = data.where(data != fill)
        if valid_range is not None:
            data = data.where((data >= valid_range[0]) & (data <= valid_range[1]))
        if factor is not None and offset is not None:
            data = data * factor + offset

        data.attrs.update(info)
        return data