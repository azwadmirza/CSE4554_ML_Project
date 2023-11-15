    def _syntax_error(self, expr, message):
        return HyTypeError(message, self.filename, expr, self.source)