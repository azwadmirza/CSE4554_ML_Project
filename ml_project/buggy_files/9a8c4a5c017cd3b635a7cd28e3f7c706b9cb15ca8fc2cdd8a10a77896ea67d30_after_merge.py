    def navigate(self, coordinate_id):
        """Get the longitudes and latitudes of the scene."""
        lons, lats = self._get_all_interpolated_coordinates()
        if coordinate_id == 'longitude':
            return create_xarray(lons)
        elif coordinate_id == 'latitude':
            return create_xarray(lats)
        else:
            raise KeyError("Coordinate {} unknown.".format(coordinate_id))