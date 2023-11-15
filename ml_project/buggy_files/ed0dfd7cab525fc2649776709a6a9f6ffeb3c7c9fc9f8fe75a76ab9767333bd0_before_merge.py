    def _on_mode_entered(self, mode):
        if mode != usertypes.KeyMode.caret:
            return

        settings = self._widget.settings()
        settings.setAttribute(QWebSettings.CaretBrowsingEnabled, True)
        self.selection_enabled = self._widget.hasSelection()

        if self._widget.isVisible():
            # Sometimes the caret isn't immediately visible, but unfocusing
            # and refocusing it fixes that.
            self._widget.clearFocus()
            self._widget.setFocus(Qt.OtherFocusReason)

            # Move the caret to the first element in the viewport if there
            # isn't any text which is already selected.
            #
            # Note: We can't use hasSelection() here, as that's always
            # true in caret mode.
            if not self.selection_enabled:
                self._widget.page().currentFrame().evaluateJavaScript(
                    utils.read_file('javascript/position_caret.js'))