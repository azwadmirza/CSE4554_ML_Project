    def _onKeyDown(self, evt):
        """Capture key press."""
        key = self._get_key(evt)
        FigureCanvasBase.key_press_event(self, key, guiEvent=evt)
        if self:
            evt.Skip()