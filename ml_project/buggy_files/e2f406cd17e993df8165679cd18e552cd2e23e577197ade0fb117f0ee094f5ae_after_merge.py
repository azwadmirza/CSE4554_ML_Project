    def add_markers(self, marker_coords, marker_color='r', marker_size=30,
                    **kwargs):
        """Add markers to the plot.

        Parameters
        ----------
        marker_coords: array of size (n_markers, 3)
            Coordinates of the markers to plot. For each slice, only markers
            that are 2 millimeters away from the slice are plotted.
        marker_color: pyplot compatible color or list of shape (n_markers,)
            List of colors for each marker that can be string or matplotlib
            colors
        marker_size: single float or list of shape (n_markers,)
            Size in pixel for each marker
        """
        defaults = {'marker': 'o',
                    'zorder': 1000}
        marker_coords = np.asanyarray(marker_coords)
        for k, v in defaults.items():
            kwargs.setdefault(k, v)

        for display_ax in self.axes.values():
            direction = display_ax.direction
            coord = display_ax.coord
            marker_coords_2d, third_d = _coords_3d_to_2d(
                marker_coords, direction, return_direction=True)
            xdata, ydata = marker_coords_2d.T
            # Check if coord has integer represents a cut in direction
            # to follow the heuristic. If no foreground image is given
            # coordinate is empty or None. This case is valid for plotting
            # markers on glass brain without any foreground image.
            if isinstance(coord, numbers.Number):
                # Heuristic that plots only markers that are 2mm away
                # from the current slice.
                # XXX: should we keep this heuristic?
                mask = np.abs(third_d - coord) <= 2.
                xdata = xdata[mask]
                ydata = ydata[mask]
            display_ax.ax.scatter(xdata, ydata, s=marker_size,
                                  c=marker_color, **kwargs)