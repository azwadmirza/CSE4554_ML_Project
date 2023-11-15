    def __init__(self, message, lineno, colno, source=None):
        super(LexException, self).__init__(message)
        self.message = message
        self.lineno = lineno
        self.colno = colno
        self.source = source
        self.filename = '<stdin>'