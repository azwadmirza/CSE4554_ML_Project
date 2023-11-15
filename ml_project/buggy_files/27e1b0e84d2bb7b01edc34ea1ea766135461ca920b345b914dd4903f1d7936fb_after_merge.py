    def current_edge_color(self, edge_color: ColorType) -> None:
        self._current_edge_color = transform_color(edge_color)
        if (
            self._update_properties
            and len(self.selected_data) > 0
            and self._mode != Mode.ADD
        ):
            cur_colors: np.ndarray = self.edge_color
            cur_colors[self.selected_data] = self._current_edge_color
            self.edge_color = cur_colors
        self.events.current_edge_color()