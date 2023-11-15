    def get_dataset(self, dataset_id, ds_info, out=None,
                    xslice=slice(None), yslice=slice(None)):
        var_name = ds_info.get('file_key', dataset_id.name)
        # FUTURE: Metadata retrieval may be separate
        i = self.get_metadata(dataset_id, ds_info)
        data = self[var_name][yslice, xslice]
        fill = self[var_name + '/attr/_FillValue']
        factor = self.get(var_name + '/attr/scale_factor')
        offset = self.get(var_name + '/attr/add_offset')
        valid_range = self.get(var_name + '/attr/valid_range')

        mask = data == fill
        if valid_range is not None:
            mask |= (data < valid_range[0]) | (data > valid_range[1])
        data = data.astype(out.data.dtype)
        if factor is not None and offset is not None:
            data *= factor
            data += offset

        out.data[:] = data
        out.mask[:] |= mask
        out.info.update(i)
        return out