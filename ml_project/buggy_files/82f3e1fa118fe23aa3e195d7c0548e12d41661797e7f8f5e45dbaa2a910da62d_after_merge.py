        def insert_text(event):
            TextEditBaseWidget.keyPressEvent(self, event)
            self.document_did_change()
            self.sig_text_was_inserted.emit()