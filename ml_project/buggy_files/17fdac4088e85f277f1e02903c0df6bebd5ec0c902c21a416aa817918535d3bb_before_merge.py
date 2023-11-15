    def __call__(self, projectables, optional_datasets=None, **info):
        """Get the corrected reflectance when removing Rayleigh scattering. Uses
        pyspectral.
        """
        from pyspectral.rayleigh import Rayleigh

        (vis, red) = projectables
        if vis.shape != red.shape:
            raise IncompatibleAreas
        try:
            (sata, satz, suna, sunz) = optional_datasets
        except ValueError:
            from pyorbital.astronomy import get_alt_az, sun_zenith_angle
            from pyorbital.orbital import get_observer_look
            lons, lats = vis.info['area'].get_lonlats()
            sunalt, suna = get_alt_az(vis.info['start_time'], lons, lats)
            suna = np.rad2deg(suna)
            sunz = sun_zenith_angle(vis.info['start_time'], lons, lats)
            sata, satel = get_observer_look(vis.info['satellite_longitude'],
                                            vis.info['satellite_latitude'],
                                            vis.info['satellite_altitude'],
                                            vis.info['start_time'],
                                            lons, lats, 0)
            satz = 90 - satel
            del satel
        LOG.info('Removing Rayleigh scattering and aerosol absorption')

        # First make sure the two azimuth angles are in the range 0-360:
        sata = np.mod(sata, 360.)
        suna = np.mod(suna, 360.)
        ssadiff = np.abs(suna - sata)
        ssadiff = np.where(ssadiff > 180, 360 - ssadiff, ssadiff)
        del sata, suna

        atmosphere = self.info.get('atmosphere', 'us-standard')
        aerosol_type = self.info.get('aerosol_type', 'marine_clean_aerosol')

        corrector = Rayleigh(vis.info['platform_name'], vis.info['sensor'],
                             atmosphere=atmosphere,
                             aerosol_type=aerosol_type)

        try:
            refl_cor_band = corrector.get_reflectance(sunz, satz, ssadiff, vis.id.name, red)
        except KeyError:
            LOG.warning("Could not get the reflectance correction using band name: %s", vis.id.name)
            LOG.warning("Will try use the wavelength, however, this may be ambiguous!")
            refl_cor_band = corrector.get_reflectance(sunz, satz, ssadiff,
                                                      vis.id.wavelength[1], red)

        proj = Dataset(vis - refl_cor_band,
                       copy=False,
                       **vis.info)
        self.apply_modifier_info(vis, proj)

        return proj