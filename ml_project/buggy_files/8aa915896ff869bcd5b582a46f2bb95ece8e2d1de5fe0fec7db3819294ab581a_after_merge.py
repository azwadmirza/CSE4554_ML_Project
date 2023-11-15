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

            if pressure_levels is True:
                cond = None
            elif len(pressure_levels) == 2:
                cond = (plevels_ds >= pressure_levels[0]) & (plevels_ds <= pressure_levels[1])
            else:
                cond = plevels_ds == pressure_levels
            if cond is not None:
                new_plevels = plevels_ds.where(cond, drop=True)
            else:
                new_plevels = plevels_ds

            for ds_id in datasets_loaded.keys():
                ds_obj = datasets_loaded[ds_id]
                if plevels_ds.dims[0] not in ds_obj.dims:
                    continue

                if cond is not None:
                    datasets_loaded[ds_id] = ds_obj.where(cond, drop=True)
                datasets_loaded[ds_id].attrs['pressure_levels'] = new_plevels

        if self.mask_surface:
            LOG.debug("Filtering pressure levels at or below the surface pressure")
            for ds_id in sorted(dataset_keys):
                ds = datasets_loaded[ds_id]
                if "surface_pressure" not in ds.attrs or "pressure_levels" not in ds.attrs:
                    continue
                data_pressure = ds.attrs["pressure_levels"]
                surface_pressure = ds.attrs["surface_pressure"]
                if isinstance(surface_pressure, float):
                    # scalar needs to become array for each record
                    surface_pressure = np.repeat(surface_pressure, ds.shape[0])
                if surface_pressure.ndim == 1 and surface_pressure.shape[0] == ds.shape[0]:
                    # surface is one element per record
                    LOG.debug("Filtering %s at and below the surface pressure", ds_id)
                    if ds.ndim == 2:
                        surface_pressure = np.repeat(surface_pressure[:, None], data_pressure.shape[0], axis=1)
                        data_pressure = np.repeat(data_pressure[None, :], surface_pressure.shape[0], axis=0)
                        datasets_loaded[ds_id] = ds.where(data_pressure < surface_pressure)
                    else:
                        # entire dataset represents one pressure level
                        data_pressure = ds.attrs["pressure_level"]
                        datasets_loaded[ds_id] = ds.where(data_pressure < surface_pressure)
                else:
                    LOG.warning("Not sure how to handle shape of 'surface_pressure' metadata")

        if self.mask_quality:
            LOG.debug("Filtering data based on quality flags")
            for ds_id in sorted(dataset_keys):
                ds = datasets_loaded[ds_id]
                if not any(x for x in ds.attrs['ancillary_variables'] if x.name == 'Quality_Flag'):
                    continue
                quality_flag = datasets_loaded['Quality_Flag']
                if quality_flag.dims[0] not in datasets_loaded[ds_id].dims:
                    continue
                LOG.debug("Masking %s where quality flag doesn't equal 1", ds_id)
                datasets_loaded[ds_id] = ds.where(quality_flag == 0)

        return datasets_loaded