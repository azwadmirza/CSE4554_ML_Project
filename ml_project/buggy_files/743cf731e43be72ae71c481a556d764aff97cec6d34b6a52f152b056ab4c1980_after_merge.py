    def _update_draw(self, scale_factors, corner_pixels, shape_threshold):
        """Update canvas scale and corner values on draw.

        For layer multiscale determing if a new resolution level or tile is
        required.

        Parameters
        ----------
        scale_factors : list
            Scale factors going from canvas to world coordinates.
        corner_pixels : array
            Coordinates of the top-left and bottom-right canvas pixels in the
            world coordinates.
        shape_threshold : tuple
            Requested shape of field of view in data coordinates.
        """
        # Note we ignore the first transform which is tile2data
        scale = np.divide(scale_factors, self._transforms[1:].simplified.scale)
        data_corners = self._transforms[1:].simplified.inverse(corner_pixels)

        self.scale_factor = np.linalg.norm(scale) / np.linalg.norm([1, 1])

        # Round and clip data corners
        data_corners = np.array(
            [np.floor(data_corners[0]), np.ceil(data_corners[1])]
        ).astype(int)
        data_corners = np.clip(
            data_corners, self._extent_data[0], self._extent_data[1]
        )

        if self.dims.ndisplay == 2 and self.multiscale:
            level, displayed_corners = compute_multiscale_level_and_corners(
                data_corners[:, self.dims.displayed],
                shape_threshold,
                self.downsample_factors[:, self.dims.displayed],
            )
            corners = np.zeros((2, self.ndim))
            corners[:, self.dims.displayed] = displayed_corners
            corners = corners.astype(int)
            if self.data_level != level or not np.all(
                self.corner_pixels == corners
            ):
                self._data_level = level
                self.corner_pixels = corners
                self.refresh()

        else:
            self.corner_pixels = data_corners