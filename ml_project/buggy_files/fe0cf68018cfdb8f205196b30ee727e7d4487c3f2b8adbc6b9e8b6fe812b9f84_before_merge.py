    def undo(self):
        """Reimplement undo to decrease text version number."""
        if self.document().isUndoAvailable():
            self.text_version -= 1
            self.skip_rstrip = True
            self.sig_undo.emit()
            TextEditBaseWidget.undo(self)
            self.sig_text_was_inserted.emit()
            self.document_did_change('')
            self.skip_rstrip = False