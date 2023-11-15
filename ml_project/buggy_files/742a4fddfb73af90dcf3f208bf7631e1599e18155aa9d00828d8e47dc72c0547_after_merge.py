    def _update_multiscale(self, corner_pixels, shape_threshold):
        """Refresh layer multiscale if new resolution level or tile is required.

        Parameters
        ----------
        corner_pixels : array
            Coordinates of the top-left and bottom-right canvas pixels in the
            data space of each layer. The length of the tuple is equal to the
            number of dimensions of the layer. If different from the current
            layer corner_pixels the layer needs refreshing.
        shape_threshold : tuple
            Requested shape of field of view in data coordinates
        """

        if len(self.dims.displayed) == 3:
            data_level = corner_pixels.shape[1] - 1
        else:
            # Clip corner pixels inside data shape
            new_corner_pixels = np.clip(
                self.corner_pixels,
                0,
                np.subtract(self.level_shapes[self.data_level], 1),
            )

            # Scale to full resolution of the data
            requested_shape = (
                new_corner_pixels[1] - new_corner_pixels[0]
            ) * self.downsample_factors[self.data_level]

            downsample_factors = self.downsample_factors[
                :, self.dims.displayed
            ]

            data_level = compute_multiscale_level(
                requested_shape[self.dims.displayed],
                shape_threshold,
                downsample_factors,
            )

        if data_level != self.data_level:
            # Set the data level, which will trigger a layer refresh and
            # further updates including recalculation of the corner_pixels
            # for the new level
            self.data_level = data_level
            self.refresh()
        elif not np.all(self.corner_pixels == corner_pixels):
            self.refresh()