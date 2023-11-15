    def redo(self):
        """Reimplement redo to increase text version number."""
        if self.document().isRedoAvailable():
            self.text_version += 1
            self.skip_rstrip = True
            TextEditBaseWidget.redo(self)
            self.document_did_change('text')
            self.sig_redo.emit()
            self.sig_text_was_inserted.emit()
            self.skip_rstrip = False