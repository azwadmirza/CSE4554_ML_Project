    def document_did_change(self, text=None):
        """Send textDocument/didChange request to the server."""
        self.text_version += 1
        text = self.toPlainText()
        self.patch = self.differ.patch_make(self.previous_text, text)
        self.previous_text = text
        params = {
            'file': self.filename,
            'version': self.text_version,
            'text': text,
            'diff': self.patch,
            'offset': self.get_position('cursor')
        }
        return params