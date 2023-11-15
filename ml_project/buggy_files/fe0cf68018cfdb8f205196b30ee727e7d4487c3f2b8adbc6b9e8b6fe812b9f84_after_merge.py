    def undo(self):
        """Reimplement undo to decrease text version number."""
        if self.document().isUndoAvailable():
            self.text_version -= 1
            self.skip_rstrip = True
            TextEditBaseWidget.undo(self)
            self.document_did_change('')
            self.sig_undo.emit()
            self.sig_text_was_inserted.emit()
            self.skip_rstrip = False