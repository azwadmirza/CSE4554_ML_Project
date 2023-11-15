    def get_dataset(self, dataset_id, ds_info):
        var_path = self._generate_file_key(dataset_id, ds_info)
        factor_var_path = ds_info.get("factors_key", var_path + "Factors")
        data = self[var_path]
        is_floating = np.issubdtype(data.dtype, np.floating)

        if is_floating:
            # If the data is a float then we mask everything <= -999.0
            fill_max = float(ds_info.pop("fill_max_float", -999.0))
            data = data.where(data > fill_max)
        else:
            # If the data is an integer then we mask everything >= fill_min_int
            fill_min = int(ds_info.pop("fill_min_int", 65528))
            data = data.where(data < fill_min)

        factors = self.get(factor_var_path)
        if factors is None:
            LOG.debug("No scaling factors found for %s", dataset_id)

        file_units = self.get_file_units(dataset_id, ds_info)
        output_units = ds_info.get("units", file_units)
        factors = self.adjust_scaling_factors(factors, file_units, output_units)

        if factors is not None:
            data = self.scale_swath_data(data, factors)

        i = getattr(data, 'attrs', {})
        i.update(ds_info)
        i.update({
            "units": ds_info.get("units", file_units),
            "platform_name": self.platform_name,
            "sensor": self.sensor_name,
            "start_orbit": self.start_orbit_number,
            "end_orbit": self.end_orbit_number,
        })
        i.update(dataset_id.to_dict())
        data.attrs.update(i)
        return data