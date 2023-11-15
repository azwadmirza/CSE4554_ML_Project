    def __init__(self, message, expression=None, filename=None, source=None,
                 lineno=1, colno=1):
        """
        Parameters
        ----------
        message: str
            The message to display for this error.
        expression: HyObject, optional
            The Hy expression generating this error.
        filename: str, optional
            The filename for the source code generating this error.
            Expression-provided information will take precedence of this value.
        source: str, optional
            The actual source code generating this error.  Expression-provided
            information will take precedence of this value.
        lineno: int, optional
            The line number of the error.  Expression-provided information will
            take precedence of this value.
        colno: int, optional
            The column number of the error.  Expression-provided information
            will take precedence of this value.
        """
        self.msg = message
        self.compute_lineinfo(expression, filename, source, lineno, colno)

        if isinstance(self, SyntaxError):
            syntax_error_args = (self.filename, self.lineno, self.offset,
                                 self.text)
            super(HyLanguageError, self).__init__(message, syntax_error_args)
        else:
            super(HyLanguageError, self).__init__(message)