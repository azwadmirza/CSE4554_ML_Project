    def __init__(self, message, lineno, colno):
        super(LexException, self).__init__(message)
        self.message = message
        self.lineno = lineno
        self.colno = colno
        self.source = None
        self.filename = '<stdin>'