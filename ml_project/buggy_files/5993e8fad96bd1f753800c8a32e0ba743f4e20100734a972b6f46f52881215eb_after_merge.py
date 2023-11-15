    def __init__(self, parent):
        QWidget.__init__(self, parent)

        self.webview = FrameWebView(self)
        self.webview.setup()

        if WEBENGINE:
            self.webview.web_widget.page().setBackgroundColor(
                QColor(MAIN_BG_COLOR))
        else:
            self.webview.web_widget.setStyleSheet(
                "background:{}".format(MAIN_BG_COLOR))
            self.viewview.page().setLinkDelegationPolicy(
                QWebEnginePage.DelegateAllLinks)

        self.find_widget = FindReplace(self)
        self.find_widget.set_editor(self.webview.web_widget)
        self.find_widget.hide()

        # Layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.webview)
        layout.addWidget(self.find_widget)
        self.setLayout(layout)

        # Signals
        self.webview.linkClicked.connect(self.sig_link_clicked)