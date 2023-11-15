    def _set_view_slice(self):
        """Set the view given the indices to slice with."""
        if self.multichannel:
            # if multichannel need to keep the final axis fixed during the
            # transpose. The index of the final axis depends on how many
            # axes are displayed.
            order = self.dims.displayed_order + (self.dims.ndisplay,)
        else:
            order = self.dims.displayed_order

        image = np.asarray(self.data[self.dims.indices]).transpose(order)

        if self.multichannel and image.dtype.kind == 'f':
            self._data_view = np.clip(image, 0, 1)
        else:
            self._data_view = image

        self._data_thumbnail = self._data_view
        self._update_thumbnail()
        self._update_coordinates()
        self.events.set_data()