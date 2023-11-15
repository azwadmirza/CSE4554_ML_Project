    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = None
        view = QWebEngineView()
        self._set_widget(view)