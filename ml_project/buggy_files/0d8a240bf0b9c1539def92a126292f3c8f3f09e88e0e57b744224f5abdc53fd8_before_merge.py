    def do_completion(self, automatic=False):
        """Trigger completion"""
        # if self.is_completion_widget_visible():
        #     return
        self.document_did_change('')
        line, column = self.get_cursor_line_column()
        params = {
            'file': self.filename,
            'line': line,
            'column': column
        }
        return params