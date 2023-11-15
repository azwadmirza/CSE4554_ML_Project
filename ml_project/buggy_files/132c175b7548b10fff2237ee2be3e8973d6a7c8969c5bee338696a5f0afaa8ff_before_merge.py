    def redo(self):
        """Reimplement redo to increase text version number."""
        if self.document().isRedoAvailable():
            self.text_version += 1
            self.skip_rstrip = True
            self.sig_redo.emit()
            TextEditBaseWidget.redo(self)
            self.sig_text_was_inserted.emit()
            self.document_did_change('text')
            self.skip_rstrip = False