    def do_completion(self, automatic=False):
        """Trigger completion"""
        self.document_did_change('')
        line, column = self.get_cursor_line_column()
        params = {
            'file': self.filename,
            'line': line,
            'column': column
        }
        return params