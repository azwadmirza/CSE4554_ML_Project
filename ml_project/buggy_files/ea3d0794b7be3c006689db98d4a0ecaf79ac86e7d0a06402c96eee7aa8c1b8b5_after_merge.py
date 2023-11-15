    def _set_view_slice(self):
        """Set the view given the indices to slice with."""
        not_disp = self.dims.not_displayed

        if self.rgb:
            # if rgb need to keep the final axis fixed during the
            # transpose. The index of the final axis depends on how many
            # axes are displayed.
            order = self.dims.displayed_order + (
                max(self.dims.displayed_order) + 1,
            )
        else:
            order = self.dims.displayed_order

        if self.multiscale:
            # If 3d redering just show lowest level of multiscale
            if self.dims.ndisplay == 3:
                self.data_level = len(self.data) - 1

            # Slice currently viewed level
            level = self.data_level
            indices = np.array(self.dims.indices)
            downsampled_indices = (
                indices[not_disp] / self.downsample_factors[level, not_disp]
            )
            downsampled_indices = np.round(
                downsampled_indices.astype(float)
            ).astype(int)
            downsampled_indices = np.clip(
                downsampled_indices, 0, self.level_shapes[level, not_disp] - 1
            )
            indices[not_disp] = downsampled_indices

            scale = np.ones(self.ndim)
            for d in self.dims.displayed:
                scale[d] = self.downsample_factors[self.data_level][d]
            self._transforms['tile2data'].scale = scale

            if self.dims.ndisplay == 2:
                corner_pixels = np.clip(
                    self.corner_pixels,
                    0,
                    np.subtract(self.level_shapes[self.data_level], 1),
                )

                for d in self.dims.displayed:
                    indices[d] = slice(
                        corner_pixels[0, d], corner_pixels[1, d] + 1, 1
                    )
                self._transforms['tile2data'].translate = (
                    corner_pixels[0]
                    * self._transforms['data2world'].scale
                    * self._transforms['tile2data'].scale
                )

            image = np.transpose(
                np.asarray(self.data[level][tuple(indices)]), order
            )

            # Slice thumbnail
            indices = np.array(self.dims.indices)
            downsampled_indices = (
                indices[not_disp]
                / self.downsample_factors[self._thumbnail_level, not_disp]
            )
            downsampled_indices = np.round(
                downsampled_indices.astype(float)
            ).astype(int)
            downsampled_indices = np.clip(
                downsampled_indices,
                0,
                self.level_shapes[self._thumbnail_level, not_disp] - 1,
            )
            indices[not_disp] = downsampled_indices
            thumbnail_source = np.asarray(
                self.data[self._thumbnail_level][tuple(indices)]
            ).transpose(order)
        else:
            self._transforms['tile2data'].scale = np.ones(self.dims.ndim)
            image = np.asarray(self.data[self.dims.indices]).transpose(order)
            thumbnail_source = image

        if self.rgb and image.dtype.kind == 'f':
            self._data_raw = np.clip(image, 0, 1)
            self._data_view = self._raw_to_displayed(self._data_raw)
            self._data_thumbnail = self._raw_to_displayed(
                np.clip(thumbnail_source, 0, 1)
            )

        else:
            self._data_raw = image
            self._data_view = self._raw_to_displayed(self._data_raw)
            self._data_thumbnail = self._raw_to_displayed(thumbnail_source)

        if self.multiscale:
            self.events.scale()
            self.events.translate()