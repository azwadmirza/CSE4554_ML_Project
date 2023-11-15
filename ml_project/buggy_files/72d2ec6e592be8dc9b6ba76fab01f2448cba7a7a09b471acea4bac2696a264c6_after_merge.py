    def _onKeyUp(self, evt):
        """Release key."""
        key = self._get_key(evt)
        FigureCanvasBase.key_release_event(self, key, guiEvent=evt)
        if self:
            evt.Skip()