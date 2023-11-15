    def _set_view_slice(self):
        """Sets the view given the indices to slice with."""

        in_slice_data, indices, scale = self._slice_data(self.dims.indices)

        # Display points if there are any in this slice
        if len(in_slice_data) > 0:
            # Get the point sizes
            sizes = (
                self.size[np.ix_(indices, self.dims.displayed)].mean(axis=1)
                * scale
            )

            # Update the points node
            data = np.array(in_slice_data)

        else:
            # if no points in this slice send dummy data
            data = np.zeros((0, self.dims.ndisplay))
            sizes = [0]
        self._data_view = data
        self._size_view = sizes
        self._indices_view = indices
        # Make sure if changing planes any selected points not in the current
        # plane are removed
        selected = []
        for c in self.selected_data:
            if c in self._indices_view:
                ind = list(self._indices_view).index(c)
                selected.append(ind)
        self._selected_view = selected
        self._set_highlight()