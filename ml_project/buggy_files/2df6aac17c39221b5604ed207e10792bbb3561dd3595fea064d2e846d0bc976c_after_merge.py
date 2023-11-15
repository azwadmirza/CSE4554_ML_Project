    def __init__(self, basename, webapp_port):
        global window_icon
        QWebView.__init__(self)
        self.setWindowTitle(u"{0} | OnionShare".format(basename.decode("utf-8")))
        self.resize(580, 400)
        self.setMinimumSize(580, 400)
        self.setMaximumSize(580, 400)
        self.setWindowIcon(window_icon)
        self.load(QUrl("http://127.0.0.1:{0}".format(webapp_port)))