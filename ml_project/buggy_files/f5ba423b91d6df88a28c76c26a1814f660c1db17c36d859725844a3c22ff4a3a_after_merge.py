    def __call__(self, projectables, optional_datasets=None, **info):
        """Get the atmospherical correction. Uses pyspectral.
        """
        from pyspectral.atm_correction_ir import AtmosphericalCorrection

        band = projectables[0]

        if optional_datasets:
            satz = optional_datasets[0]
        else:
            from pyorbital.orbital import get_observer_look
            lons, lats = band.attrs['area'].get_lonlats_dask(CHUNK_SIZE)

            try:
                dummy, satel = get_observer_look(band.attrs['satellite_longitude'],
                                                 band.attrs[
                                                     'satellite_latitude'],
                                                 band.attrs[
                                                     'satellite_altitude'],
                                                 band.attrs['start_time'],
                                                 lons, lats, 0)
            except KeyError:
                raise KeyError(
                    'Band info is missing some meta data!')
            satz = 90 - satel
            del satel

        LOG.info('Correction for limb cooling')
        corrector = AtmosphericalCorrection(band.attrs['platform_name'],
                                            band.attrs['sensor'])

        atm_corr = corrector.get_correction(satz, band.attrs['name'], band)
        proj = band - atm_corr
        proj.attrs = band.attrs
        self.apply_modifier_info(band, proj)

        return proj