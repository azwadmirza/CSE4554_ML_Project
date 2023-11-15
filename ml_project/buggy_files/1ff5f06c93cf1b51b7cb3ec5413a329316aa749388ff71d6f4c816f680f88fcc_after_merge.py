    def _set_highlight(self, force=False):
        """Render highlights of shapes including boundaries, vertices,
        interaction boxes, and the drag selection box when appropriate.
        Highlighting only occurs in Mode.SELECT.

        Parameters
        ----------
        force : bool
            Bool that forces a redraw to occur when `True`
        """
        # if self._mode == Mode.SELECT:
        # Check if any point ids have changed since last call
        if self.selected:
            if (
                self.selected_data == self._selected_data_stored
                and self._value == self._value_stored
                and np.all(self._drag_box == self._drag_box_stored)
            ) and not force:
                return
            self._selected_data_stored = copy(self.selected_data)
            self._value_stored = copy(self._value)
            self._drag_box_stored = copy(self._drag_box)

            if self._value is not None or len(self._selected_view) > 0:
                if len(self._selected_view) > 0:
                    index = copy(self._selected_view)
                    # highlight the hovered point if not in adding mode
                    if self._value is not None and self._mode != Mode.ADD:
                        hover_point = list(self._indices_view).index(
                            self._value
                        )
                        if hover_point in index:
                            pass
                        else:
                            index.append(hover_point)
                    index.sort()
                else:
                    # don't highlight hovered points in add mode
                    if self._mode != Mode.ADD:
                        hover_point = list(self._indices_view).index(
                            self._value
                        )
                        index = [hover_point]
                    else:
                        index = []

                self._highlight_index = index
            else:
                self._highlight_index = []

            # only display dragging selection box in 2D
            if self.dims.ndisplay == 2 and self._is_selecting:
                pos = create_box(self._drag_box)
                pos = pos[list(range(4)) + [0]]
            else:
                pos = None

            self._highlight_box = pos
            self.events.highlight()
        else:
            self._highlight_box = None
            self._highlight_index = []
            self.events.highlight()