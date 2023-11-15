    def get_dataset(self, key, info):
        """Get calibrated channel data."""

        if self.mdrs is None:
            self._read_all(self.filename)

        if key.name in ['longitude', 'latitude']:
            lons, lats = self.get_full_lonlats()
            # todo: make that datasets
            if key.name == 'longitude':
                return Dataset(lons, id=key, **info)
            else:
                return Dataset(lats, id=key, **info)

        if key.name in ['solar_zenith_angle', 'solar_azimuth_angle',
                        'satellite_zenith_angle', 'satellite_azimuth_angle']:
            sun_azi, sun_zen, sat_azi, sat_zen = self.get_full_angles()
            if key.name == 'solar_zenith_angle':
                return Dataset(sun_zen, id=key, **info)
            elif key.name == 'solar_azimuth_angle':
                return Dataset(sun_azi, id=key, **info)
            if key.name == 'satellite_zenith_angle':
                return Dataset(sat_zen, id=key, **info)
            elif key.name == 'satellite_azimuth_angle':
                return Dataset(sat_azi, id=key, **info)

        if key.calibration == 'counts':
            raise ValueError('calibration=counts is not supported! ' +
                             'This reader cannot return counts')
        elif key.calibration not in ['reflectance', 'brightness_temperature', 'radiance']:
            raise ValueError('calibration type ' + str(key.calibration) +
                             ' is not supported!')

        if key.name in ['3A', '3a'] and self.three_a_mask is None:
            self.three_a_mask = (
                (self["FRAME_INDICATOR"] & 2 ** 16) != 2 ** 16)

        if key.name in ['3B', '3b'] and self.three_b_mask is None:
            self.three_b_mask = ((self["FRAME_INDICATOR"] & 2 ** 16) != 0)

        if key.name not in ["1", "2", "3a", "3A", "3b", "3B", "4", "5"]:
            LOG.info("Can't load channel in eps_l1b: " + str(key.name))
            return

        if key.name == "1":
            if key.calibration == 'reflectance':
                array = np.ma.array(
                    radiance_to_refl(self["SCENE_RADIANCES"][:, 0, :],
                                     self["CH1_SOLAR_FILTERED_IRRADIANCE"]))
            else:
                array = np.ma.array(
                    self["SCENE_RADIANCES"][:, 0, :])

        if key.name == "2":
            if key.calibration == 'reflectance':
                array = np.ma.array(
                    radiance_to_refl(self["SCENE_RADIANCES"][:, 1, :],
                                     self["CH2_SOLAR_FILTERED_IRRADIANCE"]))
            else:
                array = np.ma.array(
                    self["SCENE_RADIANCES"][:, 1, :])

        if key.name.lower() == "3a":
            if key.calibration == 'reflectance':
                array = np.ma.array(
                    radiance_to_refl(self["SCENE_RADIANCES"][:, 2, :],
                                     self["CH3A_SOLAR_FILTERED_IRRADIANCE"]))
            else:
                array = np.ma.array(self["SCENE_RADIANCES"][:, 2, :])

            mask = np.empty(array.shape, dtype=bool)
            mask[:, :] = self.three_a_mask[:, np.newaxis]
            array = np.ma.array(array, mask=mask, copy=False)
        if key.name.lower() == "3b":
            if key.calibration == 'brightness_temperature':
                array = np.array(
                    radiance_to_bt(self["SCENE_RADIANCES"][:, 2, :],
                                   self["CH3B_CENTRAL_WAVENUMBER"],
                                   self["CH3B_CONSTANT1"],
                                   self["CH3B_CONSTANT2_SLOPE"]))
            else:
                array = self["SCENE_RADIANCES"][:, 2, :]
            mask = np.empty(array.shape, dtype=bool)
            mask[:, :] = self.three_b_mask[:, np.newaxis]
            array = np.ma.array(array, mask=mask, copy=False)
        if key.name == "4":
            if key.calibration == 'brightness_temperature':
                array = np.ma.array(
                    radiance_to_bt(self["SCENE_RADIANCES"][:, 3, :],
                                   self["CH4_CENTRAL_WAVENUMBER"],
                                   self["CH4_CONSTANT1"],
                                   self["CH4_CONSTANT2_SLOPE"]))
            else:
                array = np.ma.array(
                    self["SCENE_RADIANCES"][:, 3, :])

        if key.name == "5":
            if key.calibration == 'brightness_temperature':
                array = np.ma.array(
                    radiance_to_bt(self["SCENE_RADIANCES"][:, 4, :],
                                   self["CH5_CENTRAL_WAVENUMBER"],
                                   self["CH5_CONSTANT1"],
                                   self["CH5_CONSTANT2_SLOPE"]))
            else:
                array = np.ma.array(self["SCENE_RADIANCES"][:, 4, :])

        proj = Dataset(array, mask=array.mask, id=key)
        return proj