    def _set_view_slice(self):
        """Set the view given the indices to slice with."""
        nd = self.dims.not_displayed

        if self.multichannel:
            # if multichannel need to keep the final axis fixed during the
            # transpose. The index of the final axis depends on how many
            # axes are displayed.
            order = self.dims.displayed_order + (self.dims.ndisplay,)
        else:
            order = self.dims.displayed_order

        # Slice thumbnail
        indices = np.array(self.dims.indices)
        downsampled = indices[nd] / self.level_downsamples[-1, nd]
        downsampled = np.round(downsampled.astype(float)).astype(int)
        downsampled = np.clip(downsampled, 0, self.level_shapes[-1, nd] - 1)
        indices[nd] = downsampled
        self._data_thumbnail = np.asarray(
            self.data[-1][tuple(indices)]
        ).transpose(order)

        # Slice currently viewed level
        indices = np.array(self.dims.indices)
        level = self.data_level
        downsampled = indices[nd] / self.level_downsamples[level, nd]
        downsampled = np.round(downsampled.astype(float)).astype(int)
        downsampled = np.clip(downsampled, 0, self.level_shapes[level, nd] - 1)
        indices[nd] = downsampled

        disp_shape = self.level_shapes[level, self.dims.displayed]
        scale = np.ones(self.ndim)
        for d in self.dims.displayed:
            scale[d] = self.level_downsamples[self.data_level][d]
        self._scale = scale
        self.events.scale()

        if np.any(disp_shape > self._max_tile_shape):
            for d in self.dims.displayed:
                indices[d] = slice(
                    self._top_left[d],
                    self._top_left[d] + self._max_tile_shape,
                    1,
                )
            self.translate = self._top_left * self.scale
        else:
            self.translate = [0] * self.ndim

        self._data_view = np.asarray(
            self.data[level][tuple(indices)]
        ).transpose(order)

        self._update_thumbnail()
        self._update_coordinates()
        self.events.set_data()