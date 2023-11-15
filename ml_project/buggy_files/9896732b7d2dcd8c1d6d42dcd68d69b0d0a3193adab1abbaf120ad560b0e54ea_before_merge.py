    def get_full_lonlats(self):
        """Get the interpolated lons/lats."""
        if self.lons is not None and self.lats is not None:
            return self.lons, self.lats

        self.lons, self.lats = self._get_full_lonlats()
        self.lons = da.from_delayed(self.lons, dtype=self["EARTH_LOCATIONS"].dtype,
                                    shape=(self.scanlines, self.pixels))
        self.lats = da.from_delayed(self.lats, dtype=self["EARTH_LOCATIONS"].dtype,
                                    shape=(self.scanlines, self.pixels))
        return self.lons, self.lats