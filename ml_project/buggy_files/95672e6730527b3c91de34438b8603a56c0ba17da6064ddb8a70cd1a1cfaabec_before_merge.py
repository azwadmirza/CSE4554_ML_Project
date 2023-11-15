    def get_bounding_box(self):
        """Get bounding box."""
        if self.mdrs is None:
            self._read_all(self.filename)
        lats = np.hstack([self["EARTH_LOCATION_FIRST"][0, [0]],
                          self["EARTH_LOCATION_LAST"][0, [0]],
                          self["EARTH_LOCATION_LAST"][-1, [0]],
                          self["EARTH_LOCATION_FIRST"][-1, [0]]])
        lons = np.hstack([self["EARTH_LOCATION_FIRST"][0, [1]],
                          self["EARTH_LOCATION_LAST"][0, [1]],
                          self["EARTH_LOCATION_LAST"][-1, [1]],
                          self["EARTH_LOCATION_FIRST"][-1, [1]]])
        return lons.ravel(), lats.ravel()