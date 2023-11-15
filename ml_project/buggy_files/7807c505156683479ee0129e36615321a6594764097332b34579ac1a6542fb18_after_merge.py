    def __init__(self, msg="", status_code=None):
        self.msg = msg
        self.status_code = status_code
        super(WebHdfsException, self).__init__(repr(self))