    def _onKeyDown(self, evt):
        """Capture key press."""
        key = self._get_key(evt)
        evt.Skip()
        FigureCanvasBase.key_press_event(self, key, guiEvent=evt)