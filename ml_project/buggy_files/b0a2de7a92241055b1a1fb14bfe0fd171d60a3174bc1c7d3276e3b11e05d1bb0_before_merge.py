    def _get_full_angles(self):
        solar_zenith = np.hstack((self["ANGULAR_RELATIONS_FIRST"][:, [0]],
                                  self["ANGULAR_RELATIONS"][:, :, 0],
                                  self["ANGULAR_RELATIONS_LAST"][:, [0]]))

        sat_zenith = np.hstack((self["ANGULAR_RELATIONS_FIRST"][:, [1]],
                                self["ANGULAR_RELATIONS"][:, :, 1],
                                self["ANGULAR_RELATIONS_LAST"][:, [1]]))

        solar_azimuth = np.hstack((self["ANGULAR_RELATIONS_FIRST"][:, [2]],
                                   self["ANGULAR_RELATIONS"][:, :, 2],
                                   self["ANGULAR_RELATIONS_LAST"][:, [2]]))
        sat_azimuth = np.hstack((self["ANGULAR_RELATIONS_FIRST"][:, [3]],
                                 self["ANGULAR_RELATIONS"][:, :, 3],
                                 self["ANGULAR_RELATIONS_LAST"][:, [3]]))

        nav_sample_rate = self["NAV_SAMPLE_RATE"]
        earth_views_per_scanline = self["EARTH_VIEWS_PER_SCANLINE"]
        if nav_sample_rate == 20 and earth_views_per_scanline == 2048:
            from geotiepoints import metop20kmto1km
            # Note: interpolation asumes lat values values between -90 and 90
            # Solar and satellite zenith is between 0 and 180.
            solar_zenith -= 90
            sun_azi, sun_zen = metop20kmto1km(
                solar_azimuth, solar_zenith)
            sun_zen += 90
            sat_zenith -= 90
            sat_azi, sat_zen = metop20kmto1km(
                sat_azimuth, sat_zenith)
            sat_zen += 90
            return sun_azi, sun_zen, sat_azi, sat_zen
        else:
            raise NotImplementedError("Angles expansion not implemented for " +
                                      "sample rate = " + str(nav_sample_rate) +
                                      " and earth views = " +
                                      str(earth_views_per_scanline))