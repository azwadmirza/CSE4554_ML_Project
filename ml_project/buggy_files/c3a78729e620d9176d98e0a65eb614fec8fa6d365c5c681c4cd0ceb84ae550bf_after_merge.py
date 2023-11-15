    def __init__(self):
        QNetworkAccessManager.__init__(self)
        self.base_url = "http://localhost:%d/" % API_PORT
        self.reply = None
        self.status_code = -1
        self.dispatch_map = {
            'GET': self.perform_get,
            'PATCH': self.perform_patch,
            'PUT': self.perform_put,
            'DELETE': self.perform_delete,
            'POST': self.perform_post
        }
        self.on_cancel = lambda: None