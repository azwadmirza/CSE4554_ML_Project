        def insert_text(event):
            TextEditBaseWidget.keyPressEvent(self, event)
            self.sig_text_was_inserted.emit()