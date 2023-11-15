    def __call__(self, projectables, optional_datasets=None, **info):
        """Get the corrected reflectance when removing Rayleigh scattering.

        Uses pyspectral.
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
            lons, lats = vis.attrs['area'].get_lonlats_dask(CHUNK_SIZE)
            sunalt, suna = get_alt_az(vis.attrs['start_time'], lons, lats)
            suna = np.rad2deg(suna)
            sunz = sun_zenith_angle(vis.attrs['start_time'], lons, lats)
            sata, satel = get_observer_look(vis.attrs['satellite_longitude'],
                                            vis.attrs['satellite_latitude'],
                                            vis.attrs['satellite_altitude'],
                                            vis.attrs['start_time'],
                                            lons, lats, 0)
            satz = 90 - satel
            del satel
        LOG.info('Removing Rayleigh scattering and aerosol absorption')

        # First make sure the two azimuth angles are in the range 0-360:
        sata = sata % 360.
        suna = suna % 360.
        ssadiff = abs(suna - sata)
        ssadiff = xu.minimum(ssadiff, 360 - ssadiff)
        del sata, suna

        atmosphere = self.attrs.get('atmosphere', 'us-standard')
        aerosol_type = self.attrs.get('aerosol_type', 'marine_clean_aerosol')

        corrector = Rayleigh(vis.attrs['platform_name'], vis.attrs['sensor'],
                             atmosphere=atmosphere,
                             aerosol_type=aerosol_type)

        try:
            refl_cor_band = corrector.get_reflectance(sunz.load(),
                                                      satz.load(),
                                                      ssadiff,
                                                      vis.attrs['name'],
						      red.load())
        except KeyError:
            LOG.warning("Could not get the reflectance correction using band name: %s", vis.id.name)
            LOG.warning("Will try use the wavelength, however, this may be ambiguous!")
            refl_cor_band = corrector.get_reflectance(sunz.load(),
						      satz.load(),
                                                      ssadiff,
                                                      vis.attrs['wavelength'][1],
                                                      red.load())

        proj = vis - refl_cor_band
        proj.attrs = vis.attrs
        self.apply_modifier_info(vis, proj)

        return proj