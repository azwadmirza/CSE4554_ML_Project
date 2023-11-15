    def __init__(self):
        QNetworkAccessManager.__init__(self)
        self.request_id = None
        self.base_url = "http://localhost:%d/" % API_PORT
        self.reply = None
        self.generate_request_id()