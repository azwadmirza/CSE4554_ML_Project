    def __call__(self, projectables, **info):
        vis = projectables[0]
        if vis.info.get("sunz_corrected"):
            LOG.debug("Sun zen correction already applied")
            return vis

        if hasattr(vis.info["area"], 'name'):
            area_name = vis.info["area"].name
        else:
            area_name = 'swath' + str(vis.shape)
        key = (vis.info["start_time"], area_name)
        tic = time.time()
        LOG.debug("Applying sun zen correction")
        if len(projectables) == 1:
            if key not in self.coszen:
                from pyorbital.astronomy import cos_zen
                LOG.debug("Computing sun zenith angles.")
                self.coszen[key] = np.ma.masked_outside(cos_zen(vis.info["start_time"],
                                                                *vis.info["area"].get_lonlats()),
                                                        # about 88 degrees.
                                                        0.035,
                                                        1,
                                                        copy=False)
            coszen = self.coszen[key]
        else:
            coszen = np.cos(np.deg2rad(projectables[1]))

        if vis.shape != coszen.shape:
            # assume we were given lower resolution szen data than band data
            LOG.debug(
                "Interpolating coszen calculations for higher resolution band")
            factor = int(vis.shape[1] / coszen.shape[1])
            coszen = np.repeat(
                np.repeat(coszen, factor, axis=0), factor, axis=1)

        # sunz correction will be in place so we need a copy
        proj = vis.copy()
        proj = self._apply_correction(proj, coszen)
        vis.mask[coszen < 0] = True
        self.apply_modifier_info(vis, proj)
        LOG.debug(
            "Sun-zenith correction applied. Computation time: %5.1f (sec)", time.time() - tic)
        return proj