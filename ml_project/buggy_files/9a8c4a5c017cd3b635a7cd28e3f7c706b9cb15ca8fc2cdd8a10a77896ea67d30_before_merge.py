    def navigate(self):
        """Get the longitudes and latitudes of the scene."""
        lons40km = self._data["pos"][:, :, 1] * 1e-4
        lats40km = self._data["pos"][:, :, 0] * 1e-4

        try:
            from geotiepoints import SatelliteInterpolator
        except ImportError:
            logger.warning("Could not interpolate lon/lats, "
                           "python-geotiepoints missing.")
            self.lons, self.lats = lons40km, lats40km
        else:
            cols40km = np.arange(24, 2048, 40)
            cols1km = np.arange(2048)
            lines = lons40km.shape[0]
            rows40km = np.arange(lines)
            rows1km = np.arange(lines)

            along_track_order = 1
            cross_track_order = 3

            satint = SatelliteInterpolator(
                (lons40km, lats40km), (rows40km, cols40km), (rows1km, cols1km),
                along_track_order, cross_track_order)
            self.lons, self.lats = delayed(satint.interpolate, nout=2)()
            self.lons = da.from_delayed(self.lons, (lines, 2048), lons40km.dtype)
            self.lats = da.from_delayed(self.lats, (lines, 2048), lats40km.dtype)