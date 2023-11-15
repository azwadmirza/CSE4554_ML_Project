    def data(self, data: np.ndarray):
        cur_npoints = len(self._data)
        self._data = data

        # Adjust the size array when the number of points has changed
        if len(data) < cur_npoints:
            # If there are now fewer points, remove the size and colors of the
            # extra ones
            with self.events.set_data.blocker():
                self._edge_color = self.edge_color[: len(data)]
                self._face_color = self.face_color[: len(data)]
                self._size = self._size[: len(data)]

                for k in self.properties:
                    self.properties[k] = self.properties[k][: len(data)]

        elif len(data) > cur_npoints:
            # If there are now more points, add the size and colors of the
            # new ones
            with self.events.set_data.blocker():
                adding = len(data) - cur_npoints
                if len(self._size) > 0:
                    new_size = copy(self._size[-1])
                    for i in self.dims.displayed:
                        new_size[i] = self.current_size
                else:
                    # Add the default size, with a value for each dimension
                    new_size = np.repeat(
                        self.current_size, self._size.shape[1]
                    )
                size = np.repeat([new_size], adding, axis=0)

                for k in self.properties:
                    new_property = np.repeat(
                        self.current_properties[k], adding, axis=0
                    )
                    self.properties[k] = np.concatenate(
                        (self.properties[k], new_property), axis=0
                    )

                # add new edge colors
                if self._edge_color_mode == ColorMode.DIRECT:
                    new_edge_colors = np.tile(
                        self._current_edge_color, (adding, 1)
                    )
                elif self._edge_color_mode == ColorMode.CYCLE:
                    edge_color_property = self.current_properties[
                        self._edge_color_property
                    ][0]

                    # check if the new edge color property is in the cycle map
                    # and add it if it is not
                    edge_color_cycle_keys = [*self.edge_color_cycle_map]
                    if edge_color_property not in edge_color_cycle_keys:
                        self.edge_color_cycle_map[edge_color_property] = next(
                            self.edge_color_cycle
                        )

                    new_edge_colors = np.tile(
                        self.edge_color_cycle_map[edge_color_property],
                        (adding, 1),
                    )
                elif self._edge_color_mode == ColorMode.COLORMAP:
                    edge_color_property_value = self.current_properties[
                        self._edge_color_property
                    ][0]

                    ec, _ = map_property(
                        prop=edge_color_property_value,
                        colormap=self.edge_colormap[1],
                        contrast_limits=self._edge_contrast_limits,
                    )
                    new_edge_colors = np.tile(ec, (adding, 1))
                self._edge_color = np.vstack(
                    (self.edge_color, new_edge_colors)
                )

                # add new face colors
                if self._face_color_mode == ColorMode.DIRECT:
                    new_face_colors = np.tile(
                        self._current_face_color, (adding, 1)
                    )
                elif self._face_color_mode == ColorMode.CYCLE:
                    face_color_property = self.current_properties[
                        self._face_color_property
                    ][0]

                    # check if the new edge color property is in the cycle map
                    # and add it if it is not
                    face_color_cycle_keys = [*self.face_color_cycle_map]
                    if face_color_property not in face_color_cycle_keys:
                        self.face_color_cycle_map[face_color_property] = next(
                            self.face_color_cycle
                        )

                    new_face_colors = np.tile(
                        self.face_color_cycle_map[face_color_property],
                        (adding, 1),
                    )
                elif self._face_color_mode == ColorMode.COLORMAP:
                    face_color_property_value = self.current_properties[
                        self._face_color_property
                    ][0]

                    fc, _ = map_property(
                        prop=face_color_property_value,
                        colormap=self.face_colormap[1],
                        contrast_limits=self._face_contrast_limits,
                    )
                    new_face_colors = np.tile(fc, (adding, 1))
                self._face_color = np.vstack(
                    (self.face_color, new_face_colors)
                )

                self.size = np.concatenate((self._size, size), axis=0)
                self.selected_data = set(np.arange(cur_npoints, len(data)))

        self._update_dims()
        self.events.data()