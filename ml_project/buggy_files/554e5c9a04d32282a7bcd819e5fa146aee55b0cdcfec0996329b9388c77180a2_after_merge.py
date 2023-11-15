    def get_dataset(self, dataset_id, ds_info, xslice=slice(None), yslice=slice(None)):
        """Load data array and metadata from file on disk."""
        var_path = ds_info.get('file_key', '{}'.format(dataset_id.name))
        metadata = self.get_metadata(dataset_id, ds_info)
        shape = metadata['shape']
        file_shape = self[var_path + '/shape']
        if isinstance(shape, tuple) and len(shape) == 2:
            # 2D array
            if xslice.start is not None:
                shape = (shape[0], xslice.stop - xslice.start)
            if yslice.start is not None:
                shape = (yslice.stop - yslice.start, shape[1])
        elif isinstance(shape, tuple) and len(shape) == 1 and yslice.start is not None:
            shape = ((yslice.stop - yslice.start) / yslice.step,)
        metadata['shape'] = shape

        valid_min = self[var_path + '/attr/valid_min']
        valid_max = self[var_path + '/attr/valid_max']
        # no need to check fill value since we are using valid min/max
        scale_factor = self.get(var_path + '/attr/scale_factor')
        add_offset = self.get(var_path + '/attr/add_offset')

        if isinstance(file_shape, tuple) and len(file_shape) == 3:
            data = self[var_path][0, yslice, xslice]
        elif isinstance(file_shape, tuple) and len(file_shape) == 2:
            data = self[var_path][yslice, xslice]
        elif isinstance(file_shape, tuple) and len(file_shape) == 1:
            data = self[var_path][yslice]
        else:
            data = self[var_path]
        data = data.where((data >= valid_min) & (data <= valid_max))
        if scale_factor is not None:
            data = data * scale_factor + add_offset

        if ds_info.get('cloud_clear', False):
            # clear-sky if bit 15-16 are 00
            clear_sky_mask = (self['l2p_flags'][0] & 0b1100000000000000) != 0
            data = data.where(~clear_sky_mask)

        data.attrs.update(metadata)
        return data