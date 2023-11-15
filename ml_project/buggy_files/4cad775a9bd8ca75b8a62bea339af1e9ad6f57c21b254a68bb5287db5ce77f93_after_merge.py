    def _get_full_lonlats(self, lons, lats):
        nav_sample_rate = self["NAV_SAMPLE_RATE"]
        if nav_sample_rate == 20 and self.pixels == 2048:
            from geotiepoints import metop20kmto1km
            return metop20kmto1km(lons, lats)
        else:
            raise NotImplementedError("Lon/lat expansion not implemented for " +
                                      "sample rate = " + str(nav_sample_rate) +
                                      " and earth views = " +
                                      str(self.pixels))