    def __call__(self, projectables, **info):
        vis = projectables[0]
        if vis.attrs.get("sunz_corrected"):
            LOG.debug("Sun zen correction already applied")
            return vis

        if hasattr(vis.attrs["area"], 'name'):
            area_name = vis.attrs["area"].name
        else:
            area_name = 'swath' + str(vis.shape)
        key = (vis.attrs["start_time"], area_name)
        tic = time.time()
        LOG.debug("Applying sun zen correction")
        if len(projectables) == 1:
            coszen = self.coszen.get(key)
            if coszen is None:
                from pyorbital.astronomy import cos_zen
                LOG.debug("Computing sun zenith angles.")
                lons, lats = vis.attrs["area"].get_lonlats_dask(CHUNK_SIZE)

                coszen = xr.DataArray(cos_zen(vis.attrs["start_time"],
                                              lons, lats),
                                      dims=['y', 'x'],
                                      coords=[vis['y'], vis['x']])
                coszen = coszen.where((coszen > 0.035) & (coszen < 1))
                self.coszen[key] = coszen
        else:
            coszen = np.cos(np.deg2rad(projectables[1]))
            self.coszen[key] = coszen

        if vis.shape != coszen.shape:
            # assume we were given lower resolution szen data than band data
            LOG.debug(
                "Interpolating coszen calculations for higher resolution band")
            factor = int(vis.shape[1] / coszen.shape[1])
            coszen = np.repeat(
                np.repeat(coszen, factor, axis=0), factor, axis=1)

        proj = self._apply_correction(vis, coszen)
        proj.attrs = vis.attrs.copy()
        self.apply_modifier_info(vis, proj)
        LOG.debug(
            "Sun-zenith correction applied. Computation time: %5.1f (sec)",
            time.time() - tic)
        return proj