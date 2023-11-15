    def _install_event_filter(self):
        fp = self._widget.focusProxy()
        if fp is not None:
            fp.installEventFilter(self._mouse_event_filter)
        self._child_event_filter = mouse.ChildEventFilter(
            eventfilter=self._mouse_event_filter, widget=self._widget,
            parent=self)
        self._widget.installEventFilter(self._child_event_filter)