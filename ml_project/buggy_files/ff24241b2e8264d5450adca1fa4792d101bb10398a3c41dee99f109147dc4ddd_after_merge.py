    def _syntax_error(self, expr, message):
        return HySyntaxError(message, expr, self.filename, self.source)