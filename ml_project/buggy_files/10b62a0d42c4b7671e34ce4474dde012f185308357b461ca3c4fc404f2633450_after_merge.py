    def set_enabled(self, state):
        """Toggle edge line visibility."""
        self._enabled = state
        self.setVisible(state)

        # We need to request folding when toggling state so the lines
        # are computed when handling the folding response.
        self.editor.request_folding()