    def __init__(self):
        QObject.__init__(self)
        self.reply = None
        self.status_code = -1
        self.on_cancel = lambda: None