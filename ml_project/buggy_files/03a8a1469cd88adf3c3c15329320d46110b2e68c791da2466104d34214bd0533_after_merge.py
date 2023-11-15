    def __init__(self, eventfilter, widget, win_id, parent=None):
        super().__init__(parent)
        self._filter = eventfilter
        assert widget is not None
        self._widget = widget
        self._win_id = win_id