    def refresh_colors(self, update_color_mapping: bool = True):
        """Calculate and update face and edge colors if using a cycle or color map

        Parameters
        ----------
        update_color_mapping : bool
            If set to True, the function will recalculate the color cycle map
            or colormap (whichever is being used). If set to False, the function
            will use the current color cycle map or color map. For example, if you
            are adding/modifying points and want them to be colored with the same
            mapping as the other points (i.e., the new points shouldn't affect
            the color cycle map or colormap), set update_color_mapping=False.
            Default value is True.
        """
        if self._update_properties:
            if self._face_color_mode == ColorMode.CYCLE:
                face_color_properties = self.properties[
                    self._face_color_property
                ]
                if update_color_mapping:
                    self.face_color_cycle_map = {
                        k: c
                        for k, c in zip(
                            np.unique(face_color_properties),
                            self.face_color_cycle,
                        )
                    }
                face_colors = np.array(
                    [
                        self.face_color_cycle_map[x]
                        for x in face_color_properties
                    ]
                )
                self._face_color = face_colors

                self.events.face_color()
            elif self._face_color_mode == ColorMode.COLORMAP:
                face_color_properties = self.properties[
                    self._face_color_property
                ]
                if update_color_mapping:
                    face_colors, contrast_limits = map_property(
                        prop=face_color_properties,
                        colormap=self.face_colormap[1],
                    )
                    self.face_contrast_limits = contrast_limits
                else:
                    face_colors, _ = map_property(
                        prop=face_color_properties,
                        colormap=self.face_colormap[1],
                        contrast_limits=self.face_contrast_limits,
                    )
                self._face_color = face_colors

            if self._edge_color_mode == ColorMode.CYCLE:
                edge_color_properties = self.properties[
                    self._edge_color_property
                ]
                if update_color_mapping:
                    self.edge_color_cycle_map = {
                        k: c
                        for k, c in zip(
                            np.unique(edge_color_properties),
                            self.edge_color_cycle,
                        )
                    }
                edge_colors = np.array(
                    [
                        self.edge_color_cycle_map[x]
                        for x in edge_color_properties
                    ]
                )
                self._edge_color = edge_colors
            elif self._edge_color_mode == ColorMode.COLORMAP:
                edge_color_properties = self.properties[
                    self._edge_color_property
                ]
                if update_color_mapping:
                    edge_colors, contrast_limits = map_property(
                        prop=edge_color_properties,
                        colormap=self.edge_colormap[1],
                    )
                    self.edge_contrast_limits = contrast_limits
                else:
                    edge_colors, _ = map_property(
                        prop=edge_color_properties,
                        colormap=self.edge_colormap[1],
                        contrast_limits=self.edge_contrast_limits,
                    )

                self._edge_color = edge_colors
            self.events.face_color()
            self.events.edge_color()