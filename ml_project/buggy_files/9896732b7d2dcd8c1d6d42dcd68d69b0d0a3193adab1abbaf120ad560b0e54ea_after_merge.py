    def get_full_lonlats(self):
        """Get the interpolated lons/lats."""
        if self.lons is not None and self.lats is not None:
            return self.lons, self.lats

        raw_lats = np.hstack((self["EARTH_LOCATION_FIRST"][:, [0]],
                              self["EARTH_LOCATIONS"][:, :, 0],
                              self["EARTH_LOCATION_LAST"][:, [0]]))

        raw_lons = np.hstack((self["EARTH_LOCATION_FIRST"][:, [1]],
                              self["EARTH_LOCATIONS"][:, :, 1],
                              self["EARTH_LOCATION_LAST"][:, [1]]))
        self.lons, self.lats = self._get_full_lonlats(raw_lons, raw_lats)
        self.lons = da.from_delayed(self.lons, dtype=self["EARTH_LOCATIONS"].dtype,
                                    shape=(self.scanlines, self.pixels))
        self.lats = da.from_delayed(self.lats, dtype=self["EARTH_LOCATIONS"].dtype,
                                    shape=(self.scanlines, self.pixels))
        return self.lons, self.lats