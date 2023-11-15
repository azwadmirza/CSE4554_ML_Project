    def get_dataset(self, dataset_id, ds_info, out=None, xslice=slice(None), yslice=slice(None)):
        """Load data array and metadata from file on disk."""
        var_path = ds_info.get('file_key', '{}'.format(dataset_id.name))
        dtype = ds_info.get('dtype', np.float32)
        cls = ds_info.pop("container", Dataset)
        if var_path + '/shape' not in self:
            # loading a scalar value
            shape = 1
        else:
            file_shape = shape = self[var_path + '/shape']
            if len(shape) == 3:
                if shape[0] != 1:
                    raise ValueError("Not sure how to load 3D Dataset with more than 1 time")
                else:
                    shape = shape[1:]

        if isinstance(shape, tuple) and len(shape) == 2:
            # 2D array
            if xslice.start is not None:
                shape = (shape[0], xslice.stop - xslice.start)
            if yslice.start is not None:
                shape = (yslice.stop - yslice.start, shape[1])
        elif isinstance(shape, tuple) and len(shape) == 1 and yslice.start is not None:
            shape = ((yslice.stop - yslice.start) / yslice.step,)

        if out is None:
            out = cls(np.ma.empty(shape, dtype=dtype),
                      mask=np.zeros(shape, dtype=np.bool),
                      copy=False)

        valid_min = self[var_path + '/attr/valid_min']
        valid_max = self[var_path + '/attr/valid_max']
        # no need to check fill value since we are using valid min/max
        scale_factor = self.get(var_path + '/attr/scale_factor')
        add_offset = self.get(var_path + '/attr/add_offset')

        if isinstance(file_shape, tuple) and len(file_shape) == 3:
            out.data[:] = np.require(self[var_path][0, yslice, xslice], dtype=dtype)
        elif isinstance(file_shape, tuple) and len(file_shape) == 2:
            out.data[:] = np.require(self[var_path][yslice, xslice], dtype=dtype)
        elif isinstance(file_shape, tuple) and len(file_shape) == 1:
            out.data[:] = np.require(self[var_path][yslice], dtype=dtype)
        else:
            out.data[:] = np.require(self[var_path][:], dtype=dtype)
        out.mask[:] = (out.data < valid_min) | (out.data > valid_max)
        if scale_factor is not None:
            out.data[:] *= scale_factor
            out.data[:] += add_offset

        if ds_info.get('cloud_clear', False):
            # clear-sky if bit 15-16 are 00
            clear_sky_mask = (self['l2p_flags'][0, :, :] & 0b1100000000000000) != 0
            out.mask[:] |= clear_sky_mask

        units = self[var_path + '/attr/units']
        standard_name = self[var_path + '/attr/standard_name']
        resolution = float(self['/attr/spatial_resolution'].split(' ')[0])
        rows_per_scan = ROWS_PER_SCAN.get(self.sensor_name) or 0
        out.info.update(dataset_id.to_dict())
        out.info.update({
            'units': units,
            'platform': self.platform_name,
            'sensor': self.sensor_name,
            'standard_name': standard_name,
            'resolution': resolution,
            'rows_per_scan': rows_per_scan,
            'long_name': self.get(var_path + '/attr/long_name'),
            'comment': self.get(var_path + '/attr/comment'),
        })
        return out