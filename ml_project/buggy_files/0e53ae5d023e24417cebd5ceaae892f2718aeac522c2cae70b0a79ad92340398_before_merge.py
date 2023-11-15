    def __call__(self, transform_xy, x1, y1, x2, y2):
        x_, y_ = np.linspace(x1, x2, self.nx), np.linspace(y1, y2, self.ny)
        x, y = np.meshgrid(x_, y_)
        lon, lat = transform_xy(np.ravel(x), np.ravel(y))

        with np.errstate(invalid='ignore'):
            if self.lon_cycle is not None:
                lon0 = np.nanmin(lon)
                # Changed from 180 to 360 to be able to span only
                # 90-270 (left hand side)
                lon -= 360. * ((lon - lon0) > 360.)
            if self.lat_cycle is not None:
                lat0 = np.nanmin(lat)
                # Changed from 180 to 360 to be able to span only
                # 90-270 (left hand side)
                lat -= 360. * ((lat - lat0) > 360.)

        lon_min, lon_max = np.nanmin(lon), np.nanmax(lon)
        lat_min, lat_max = np.nanmin(lat), np.nanmax(lat)

        lon_min, lon_max, lat_min, lat_max = \
            self._adjust_extremes(lon_min, lon_max, lat_min, lat_max)

        return lon_min, lon_max, lat_min, lat_max