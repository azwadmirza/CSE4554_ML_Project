    def __init__(self, e):
        self.code = e.response.status_code
        self.headers = e.response.headers
        Exception.__init__(self, "{}. Response: {}".format(e, e.response.text))