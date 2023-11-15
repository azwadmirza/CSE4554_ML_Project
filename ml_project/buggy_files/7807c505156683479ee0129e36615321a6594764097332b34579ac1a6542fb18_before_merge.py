    def __init__(self, msg=str()):
        self.msg = msg
        super(WebHdfsException, self).__init__(self.msg)