    def get_area_def(self, key):
        """Get the area definition of the data at hand."""
        projection = self.nc["goes_imager_projection"]
        a = projection.attrs['semi_major_axis'][...]
        h = projection.attrs['perspective_point_height'][...]
        b = projection.attrs['semi_minor_axis'][...]
        lon_0 = projection.attrs['longitude_of_projection_origin'][...]
        sweep_axis = projection.attrs['sweep_angle_axis'].decode()

        # need 64-bit floats otherwise small shift
        scale_x = np.float64(self.nc['x'].attrs["scale_factor"][0])
        scale_y = np.float64(self.nc['y'].attrs["scale_factor"][0])
        offset_x = np.float64(self.nc['x'].attrs["add_offset"][0])
        offset_y = np.float64(self.nc['y'].attrs["add_offset"][0])

        # x and y extents in m
        h = float(h)
        x_l = h * (self.nc['x'][0] * scale_x + offset_x)
        x_r = h * (self.nc['x'][-1] * scale_x + offset_x)
        y_l = h * (self.nc['y'][-1] * scale_y + offset_y)
        y_u = h * (self.nc['y'][0] * scale_y + offset_y)
        x_half = (x_r - x_l) / (self.ncols - 1) / 2.
        y_half = (y_u - y_l) / (self.nlines - 1) / 2.
        area_extent = (x_l - x_half, y_l - y_half, x_r + x_half, y_u + y_half)

        proj_dict = {'a': float(a),
                     'b': float(b),
                     'lon_0': float(lon_0),
                     'h': h,
                     'proj': 'geos',
                     'units': 'm',
                     'sweep': sweep_axis}

        area = geometry.AreaDefinition(
            'some_area_name',
            "On-the-fly area",
            'geosabii',
            proj_dict,
            self.ncols,
            self.nlines,
            area_extent)

        return area