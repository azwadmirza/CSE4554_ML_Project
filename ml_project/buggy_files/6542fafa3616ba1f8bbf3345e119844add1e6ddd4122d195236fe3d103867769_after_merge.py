    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = None
        view = QWebEngineView()
        settings = view.settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        self._set_widget(view)