    def has_selected_text(self):
        """Returns True if some text is selected."""
        return bool(to_text_string(self.textCursor().selectedText()))