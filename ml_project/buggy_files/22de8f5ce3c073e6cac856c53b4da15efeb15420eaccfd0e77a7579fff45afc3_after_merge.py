    def hideEvent(self, event):
        """ Reimplemented to disconnect signal handlers and event filter.
        """
        super(CallTipWidget, self).hideEvent(event)
        # This is needed for issue spyder-ide/spyder#9221
        try:
            self._text_edit.cursorPositionChanged.disconnect(
                self._cursor_position_changed)
        except TypeError:
            pass
        self._text_edit.removeEventFilter(self)