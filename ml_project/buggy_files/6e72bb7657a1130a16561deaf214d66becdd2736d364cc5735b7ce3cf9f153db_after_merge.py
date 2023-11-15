    def on_key_press(self, event):
        """Called whenever key pressed in canvas.
        """
        if event.native.isAutoRepeat():
            return
        else:
            if event.key == ' ':
                if self._mode != Mode.PAN_ZOOM:
                    self._mode_history = self.mode
                    self._selected_data_history = copy(self.selected_data)
                    self.mode = Mode.PAN_ZOOM
                else:
                    self._mode_history = Mode.PAN_ZOOM
            elif event.key == 'Shift':
                if self._mode == Mode.ADD:
                    self.cursor = 'forbidden'
            elif event.key == 'p':
                self.mode = Mode.ADD
            elif event.key == 's':
                self.mode = Mode.SELECT
            elif event.key == 'z':
                self.mode = Mode.PAN_ZOOM
            elif event.key == 'c' and 'Control' in event.modifiers:
                if self._mode == Mode.SELECT:
                    self._copy_data()
            elif event.key == 'v' and 'Control' in event.modifiers:
                if self._mode == Mode.SELECT:
                    self._paste_data()
            elif event.key == 'a':
                if self._mode == Mode.SELECT:
                    self.selected_data = self._indices_view[
                        : len(self._data_view)
                    ]
                    self._set_highlight()
            elif event.key == 'Backspace':
                if self._mode == Mode.SELECT:
                    self.remove_selected()