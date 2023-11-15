    def load(self, dataset_keys, pressure_levels=None):
        """Load data from one or more set of files.

        :param pressure_levels: mask out certain pressure levels:
                                True for all levels
                                (min, max) for a range of pressure levels
                                [...] list of levels to include
        """
        dataset_keys = set(self.get_dataset_key(x) for x in dataset_keys)
        if pressure_levels is not None:
            # Filter out datasets that don't fit in the correct pressure level
            for ds_id in dataset_keys.copy():
                ds_info = self.ids[ds_id]
                ds_level = ds_info.get("pressure_level")
                if ds_level is not None:
                    if pressure_levels is True:
                        # they want all pressure levels
                        continue
                    elif len(pressure_levels) == 2 and pressure_levels[0] <= ds_level <= pressure_levels[1]:
                        # given a min and a max pressure level
                        continue
                    elif np.isclose(pressure_levels, ds_level).any():
                        # they asked for this specific pressure level
                        continue
                    else:
                        # they don't want this dataset at this pressure level
                        LOG.debug("Removing dataset to load: %s", ds_id)
                        dataset_keys.remove(ds_id)
                        continue

            # Add pressure levels to the datasets to load if needed so
            # we can do further filtering after loading
            plevels_ds_id = self.get_dataset_key('Pressure_Levels')
            remove_plevels = False
            if plevels_ds_id not in dataset_keys:
                dataset_keys.add(plevels_ds_id)
                remove_plevels = True

        datasets_loaded = super(NUCAPSReader, self).load(dataset_keys)

        if pressure_levels is not None:
            if remove_plevels:
                plevels_ds = datasets_loaded.pop(plevels_ds_id)
                dataset_keys.remove(plevels_ds_id)
            else:
                plevels_ds = datasets_loaded[plevels_ds_id]

            for ds_id in datasets_loaded.keys():
                ds_obj = datasets_loaded[ds_id]
                if plevels_ds is None:
                    LOG.debug("No 'pressure_levels' metadata included in dataset")
                    continue
                if plevels_ds.shape[0] != ds_obj.shape[-1]:
                    # LOG.debug("Dataset '{}' doesn't contain multiple pressure levels".format(ds_id))
                    continue

                if pressure_levels is True:
                    levels_mask = np.ones(plevels_ds.shape, dtype=np.bool)
                elif len(pressure_levels) == 2:
                    # given a min and a max pressure level
                    levels_mask = (plevels_ds <= pressure_levels[1]) & (plevels_ds >= pressure_levels[0])
                else:
                    levels_mask = np.zeros(plevels_ds.shape, dtype=np.bool)
                    for idx, ds_level in enumerate(plevels_ds):
                        levels_mask[idx] = np.isclose(pressure_levels, ds_level).any()

                datasets_loaded[ds_id] = ds_obj[..., levels_mask]
                datasets_loaded[ds_id].info["pressure_levels"] = plevels_ds[levels_mask]

        if self.mask_surface:
            LOG.debug("Filtering pressure levels at or below the surface pressure")
            for ds_id in sorted(dataset_keys):
                ds = datasets_loaded[ds_id]
                if "surface_pressure" not in ds.info or "pressure_levels" not in ds.info:
                    continue
                data_pressure = ds.info["pressure_levels"]
                surface_pressure = ds.info["surface_pressure"]
                if isinstance(surface_pressure, float):
                    # scalar needs to become array for each record
                    surface_pressure = np.repeat(surface_pressure, ds.shape[0])
                if surface_pressure.ndim == 1 and surface_pressure.shape[0] == ds.shape[0]:
                    # surface is one element per record
                    LOG.debug("Filtering %s at and below the surface pressure", ds_id)
                    if ds.ndim == 2:
                        surface_pressure = np.repeat(surface_pressure[:, None], data_pressure.shape[0], axis=1)
                        data_pressure = np.repeat(data_pressure[None, :], surface_pressure.shape[0], axis=0)
                        ds.mask[data_pressure >= surface_pressure] = True
                    else:
                        # entire dataset represents one pressure level
                        data_pressure = ds.info["pressure_level"]
                        ds.mask[data_pressure >= surface_pressure] = True
                else:
                    LOG.warning("Not sure how to handle shape of 'surface_pressure' metadata")

        if self.mask_quality:
            LOG.debug("Filtering data based on quality flags")
            for ds_id in sorted(dataset_keys):
                ds = datasets_loaded[ds_id]
                if "quality_flag" not in ds.info:
                    continue
                quality_flag = ds.info["quality_flag"]
                LOG.debug("Masking %s where quality flag doesn't equal 1", ds_id)
                ds.mask[quality_flag != 0, ...] = True

        return datasets_loaded