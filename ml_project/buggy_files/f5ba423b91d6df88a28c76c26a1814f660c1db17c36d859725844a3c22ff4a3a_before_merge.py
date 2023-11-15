    def __call__(self, projectables, optional_datasets=None, **info):
        """Get the atmospherical correction. Uses pyspectral.
        """
        from pyspectral.atm_correction_ir import AtmosphericalCorrection

        band = projectables[0]

        if optional_datasets:
            satz = optional_datasets[0]
        else:
            from pyorbital.orbital import get_observer_look
            lons, lats = band.info['area'].get_lonlats()

            try:
                dummy, satel = get_observer_look(band.info['satellite_longitude'],
                                                 band.info[
                                                     'satellite_latitude'],
                                                 band.info[
                                                     'satellite_altitude'],
                                                 band.info['start_time'],
                                                 lons, lats, 0)
            except KeyError:
                raise KeyError(
                    'Band info is missing some meta data!')
            satz = 90 - satel
            del satel

        LOG.info('Correction for limb cooling')
        corrector = AtmosphericalCorrection(band.info['platform_name'],
                                            band.info['sensor'])

        atm_corr = corrector.get_correction(satz, band.info['name'], band)

        proj = Dataset(atm_corr,
                       copy=False,
                       **band.info)
        self.apply_modifier_info(band, proj)

        return proj