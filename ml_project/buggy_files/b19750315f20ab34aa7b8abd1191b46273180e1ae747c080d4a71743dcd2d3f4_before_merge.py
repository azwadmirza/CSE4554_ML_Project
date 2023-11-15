    def get_dataset(self, dataset_id, ds_info):
        dataset_group = [ds_group for ds_group in ds_info['dataset_groups'] if ds_group in self.datasets]
        if not dataset_group:
            return
        else:
            dataset_group = dataset_group[0]
            ds_info['dataset_group'] = dataset_group
        var_path = self._generate_file_key(dataset_id, ds_info)
        factor_var_path = ds_info.get("factors_key", var_path + "Factors")

        data = self.concatenate_dataset(dataset_group, var_path)
        data = self.mask_fill_values(data, ds_info)
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