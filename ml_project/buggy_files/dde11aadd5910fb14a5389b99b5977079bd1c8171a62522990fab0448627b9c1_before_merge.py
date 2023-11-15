    def get_full_angles(self):
        """Get the interpolated lons/lats."""
        if (self.sun_azi is not None and self.sun_zen is not None and
                self.sat_azi is not None and self.sat_zen is not None):
            return self.sun_azi, self.sun_zen, self.sat_azi, self.sat_zen

        self.sun_azi, self.sun_zen, self.sat_azi, self.sat_zen = self._get_full_angles()
        self.sun_azi = da.from_delayed(self.sun_azi, dtype=self["ANGULAR_RELATIONS"].dtype,
                                       shape=(self.scanlines, self.pixels))
        self.sun_zen = da.from_delayed(self.sun_zen, dtype=self["ANGULAR_RELATIONS"].dtype,
                                       shape=(self.scanlines, self.pixels))
        self.sat_azi = da.from_delayed(self.sat_azi, dtype=self["ANGULAR_RELATIONS"].dtype,
                                       shape=(self.scanlines, self.pixels))
        self.sat_zen = da.from_delayed(self.sat_zen, dtype=self["ANGULAR_RELATIONS"].dtype,
                                       shape=(self.scanlines, self.pixels))
        return self.sun_azi, self.sun_zen, self.sat_azi, self.sat_zen