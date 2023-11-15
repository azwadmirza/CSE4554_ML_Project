    def _set_highlight(self, force=False):
        """Render highlights of shapes including boundaries, vertices,
        interaction boxes, and the drag selection box when appropriate

        Parameters
        ----------
        force : bool
            Bool that forces a redraw to occur when `True`
        """
        # Check if any point ids have changed since last call
        if (
            self.selected_data == self._selected_data_stored
            and self._value == self._value_stored
            and np.all(self._drag_box == self._drag_box_stored)
        ) and not force:
            return
        self._selected_data_stored = copy(self.selected_data)
        self._value_stored = copy(self._value)
        self._drag_box_stored = copy(self._drag_box)

        if self._mode == Mode.SELECT and (
            self._value is not None or len(self._selected_view) > 0
        ):
            if len(self._selected_view) > 0:
                index = copy(self._selected_view)
                if self._value is not None:
                    hover_point = list(self._indices_view).index(self._value)
                    if hover_point in index:
                        pass
                    else:
                        index.append(hover_point)
                index.sort()
            else:
                hover_point = list(self._indices_view).index(self._value)
                index = [hover_point]

            self._highlight_index = index
        else:
            self._highlight_index = []

        pos = self._selected_box
        if pos is None and not self._is_selecting:
            pos = np.zeros((0, 2))
        elif self._is_selecting:
            pos = create_box(self._drag_box)
            pos = pos[list(range(4)) + [0]]
        else:
            pos = pos[list(range(4)) + [0]]

        self._highlight_box = pos
        self.events.highlight()