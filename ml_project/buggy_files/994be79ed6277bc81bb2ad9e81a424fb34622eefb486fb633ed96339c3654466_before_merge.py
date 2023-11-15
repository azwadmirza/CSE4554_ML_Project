    def __init__(self, code=None, msg=None):
        if code is not None and msg is None:
            msg = self.CODES.get(code) and 'unknown error'
        super(ProxyError, self).__init__(code, msg)