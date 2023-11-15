    def __init__(self, window=None):
        QObject.__init__(self)
        self.window = window
        self.reply = None
        self.status_code = -1
        self.on_cancel = lambda: None