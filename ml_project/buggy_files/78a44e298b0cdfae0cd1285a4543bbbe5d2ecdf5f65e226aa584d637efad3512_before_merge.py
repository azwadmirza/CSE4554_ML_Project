    def __init__(self, message, filename=None, lineno=-1, colno=-1,
                 source=None):
        """
        Parameters
        ----------
        message: str
            The exception's message.
        filename: str, optional
            The filename for the source code generating this error.
        lineno: int, optional
            The line number of the error.
        colno: int, optional
            The column number of the error.
        source: str, optional
            The actual source code generating this error.
        """
        self.message = message
        self.filename = filename
        self.lineno = lineno
        self.colno = colno
        self.source = source
        super(HySyntaxError, self).__init__(message,
                                            # The builtin `SyntaxError` needs a
                                            # tuple.
                                            (filename, lineno, colno, source))