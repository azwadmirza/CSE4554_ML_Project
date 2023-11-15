    def _get_full_angles(self, solar_zenith, sat_zenith, solar_azimuth, sat_azimuth):

        nav_sample_rate = self["NAV_SAMPLE_RATE"]
        if nav_sample_rate == 20 and self.pixels == 2048:
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
                                      str(self.pixels))