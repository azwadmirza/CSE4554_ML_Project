    def on_mouse_press(self, event):
        """Called whenever mouse pressed in canvas.

        Parameters
        ----------
        event : Event
            Vispy event
        """
        if self._mode == Mode.PAN_ZOOM:
            # If in pan/zoom mode do nothing
            pass
        elif self._mode == Mode.PICKER:
            self.selected_label = self._value or 0
        elif self._mode == Mode.PAINT:
            # Start painting with new label
            self._save_history()
            self._block_saving = True
            self.paint(self.coordinates, self.selected_label)
            self._last_cursor_coord = copy(self.coordinates)
        elif self._mode == Mode.FILL:
            # Fill clicked on region with new label
            self.fill(self.coordinates, self._value, self.selected_label)
        else:
            raise ValueError("Mode not recongnized")