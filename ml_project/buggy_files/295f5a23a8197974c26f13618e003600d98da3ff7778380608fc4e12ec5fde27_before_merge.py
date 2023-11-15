    def get_dataset(self, dataset_id, ds_info, out=None):
        var_path = self._generate_file_key(dataset_id, ds_info)
        factor_var_path = ds_info.get("factors_key", var_path + "Factors")
        data = self[var_path]
        dtype = ds_info.get("dtype", np.float32)
        is_floating = np.issubdtype(data.dtype, np.floating)
        if out is not None:
            # This assumes that we are promoting the dtypes (ex. float file data -> int array)
            # and that it happens automatically when assigning to the existing
            # out array
            out.data[:] = data
        else:
            shape = self.get_shape(dataset_id, ds_info)
            out = np.ma.empty(shape, dtype=dtype)
            out.mask = np.zeros(shape, dtype=np.bool)

        if is_floating:
            # If the data is a float then we mask everything <= -999.0
            fill_max = float(ds_info.pop("fill_max_float", -999.0))
            out.mask[:] |= out.data <= fill_max
        else:
            # If the data is an integer then we mask everything >= fill_min_int
            fill_min = int(ds_info.pop("fill_min_int", 65528))
            out.mask[:] |= out.data >= fill_min

        factors = self.get(factor_var_path)
        if factors is None:
            LOG.debug("No scaling factors found for %s", dataset_id)

        file_units = self.get_file_units(dataset_id, ds_info)
        output_units = ds_info.get("units", file_units)
        factors = self.adjust_scaling_factors(factors, file_units, output_units)

        if factors is not None:
            self.scale_swath_data(out.data, out.mask, factors)

        i = getattr(out, 'info', {})
        i.update(ds_info)
        i.update({
            "units": ds_info.get("units", file_units),
            "platform_name": self.platform_name,
            "sensor": self.sensor_name,
            "start_orbit": self.start_orbit_number,
            "end_orbit": self.end_orbit_number,
        })
        i.update(dataset_id.to_dict())
        cls = ds_info.pop("container", Dataset)
        return cls(out.data, mask=out.mask, copy=False, **i)