    def __init__(self, http_error):
        self.code = http_error.code
        self.headers = http_error.headers
        msg = http_error.msg + ": " + http_error.read()
        Exception.__init__(self, msg)