    def edge_color(self, edge_color):
        # if the provided face color is a string, first check if it is a key in the properties.
        # otherwise, assume it is the name of a color
        if self._is_color_mapped(edge_color):
            if guess_continuous(self.properties[edge_color]):
                self._edge_color_mode = ColorMode.COLORMAP
            else:
                self._edge_color_mode = ColorMode.CYCLE
            self._edge_color_property = edge_color
            self.refresh_colors()

        else:
            transformed_color = transform_color_with_defaults(
                num_entries=len(self.data),
                colors=edge_color,
                elem_name="edge_color",
                default="white",
            )
            self._edge_color = normalize_and_broadcast_colors(
                len(self.data), transformed_color
            )
            self.edge_color_mode = ColorMode.DIRECT
            self._edge_color_property = ''

            self.events.edge_color()
            self.events.highlight()