    def hideEvent(self, event):
        """ Reimplemented to disconnect signal handlers and event filter.
        """
        super(CallTipWidget, self).hideEvent(event)
        self._text_edit.cursorPositionChanged.disconnect(
            self._cursor_position_changed)
        self._text_edit.removeEventFilter(self)