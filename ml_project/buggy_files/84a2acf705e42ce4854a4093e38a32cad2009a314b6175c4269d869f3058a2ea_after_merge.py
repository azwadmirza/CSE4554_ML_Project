    def selected_data(self, selected_data):
        self._selected_data = set(selected_data)
        selected = []
        for c in self._selected_data:
            if c in self._indices_view:
                ind = list(self._indices_view).index(c)
                selected.append(ind)
        self._selected_view = selected

        # Update properties based on selected points
        if len(self._selected_data) == 0:
            self._set_highlight()
            return
        index = list(self._selected_data)
        edge_colors = np.unique(self.edge_color[index], axis=0)
        if len(edge_colors) == 1:
            edge_color = edge_colors[0]
            with self.block_update_properties():
                self.current_edge_color = edge_color

        face_colors = np.unique(self.face_color[index], axis=0)
        if len(face_colors) == 1:
            face_color = face_colors[0]
            with self.block_update_properties():
                self.current_face_color = face_color

        size = list(
            set([self.size[i, self.dims.displayed].mean() for i in index])
        )
        if len(size) == 1:
            size = size[0]
            with self.block_update_properties():
                self.current_size = size

        properties = {
            k: np.unique(v[index], axis=0) for k, v in self.properties.items()
        }
        n_unique_properties = np.array([len(v) for v in properties.values()])
        if np.all(n_unique_properties == 1):
            with self.block_update_properties():
                self.current_properties = properties
        self._set_highlight()